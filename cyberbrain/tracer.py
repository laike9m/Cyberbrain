"""Cyberbrain public API and tracer setup."""

import argparse
import dis
import functools
import os
import sys
from types import MethodType, FunctionType, FrameType
from typing import Optional, Union

from get_port import get_port

from . import logger, utils, rpc_server
from .frame import Frame
from .frame_tree import FrameTree

_debug_mode = False

# This is to allow using debug mode in both test and non-test code.
# Flag will conflict, so only execute it if not running a test.
if not utils.run_in_test():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--debug_mode",
        dest="debug_mode",
        action="store_true",
        help="Whether to log more stuff for debugging.",
    )
    parser.set_defaults(debug_mode=False)
    cb_args, _ = parser.parse_known_args()
    _debug_mode = cb_args.debug_mode


class TracerFSM:
    # States
    INITIAL = 0
    ACTIVE = 1
    CALLED = 2

    # Operations
    START = 3
    STOP = 4

    mapping = {(INITIAL, START): ACTIVE, (ACTIVE, STOP): CALLED}

    @classmethod
    def next_state(cls, current_state, operation):
        return cls.mapping[(current_state, operation)]


class Tracer:

    debug_mode = _debug_mode

    def __init__(self, debug_mode=None):
        self.frame = None
        self.raw_frame = None
        self.decorated_function_code_id = None
        self.frame_logger: Optional[logger.FrameLogger] = None
        if debug_mode is not None:
            self.debug_mode = debug_mode

        self.tracer_state = TracerFSM.INITIAL

        # For now server is put inside Tracer. Later when we need to trace multiple
        # frames it should be moved to somewhere else.
        self.server = rpc_server.Server()
        if utils.run_in_test():
            # Picks a random port for testing to allow concurrent test execution.
            self.server.serve(port=get_port())
        else:
            self.server.serve()

    def _initialize_frame_and_logger(
        self, raw_frame: FrameType, initial_instr_pointer: int
    ):
        self.tracer_state = TracerFSM.next_state(self.tracer_state, TracerFSM.START)
        frame_name = (
            # Use filename as frame name if code is run at module level.
            os.path.basename(raw_frame.f_code.co_filename).rstrip(".py")
            if raw_frame.f_code.co_name == "<module>"
            else raw_frame.f_code.co_name
        )
        self.frame = Frame(
            # For testing, only stores the basename so it's separator agnostic.
            filename=utils.shorten_path(
                raw_frame.f_code.co_filename, 1 if utils.run_in_test() else 3
            ),
            frame_name=frame_name,
            offset_to_lineno=utils.map_bytecode_offset_to_lineno(raw_frame),
        )
        FrameTree.add_frame(self.frame.frame_id, self.frame)
        self.frame_logger = logger.FrameLogger(
            instructions={
                instr.offset: instr for instr in dis.get_instructions(raw_frame.f_code)
            },
            initial_instr_pointer=initial_instr_pointer,
            frame=self.frame,
            debug_mode=self.debug_mode,
        )

    def start(self, *, disabled=False):
        """Initializes tracing."""

        # For now, we only allow triggering tracing once. This might change in the
        # future.
        if disabled or self.tracer_state != TracerFSM.INITIAL:
            return

        self.raw_frame = sys._getframe(1)
        # tracer.init() contains the following instructions:
        #               0 LOAD_FAST                0 (tracer)
        #               2 LOAD_METHOD              0 (init)
        #               4 CALL_METHOD              0
        #               6 POP_TOP
        # However logger is initialized before executing CALL_METHOD, last_i is already
        # at 4. This will make value stack don't have enough elements. So we need to
        # move the instr_pointer back to LOAD_FAST, and make sure LOAD_FAST and
        # LOAD_METHOD are scanned, so that value stack can be in correct state.
        self._initialize_frame_and_logger(
            self.raw_frame, initial_instr_pointer=self.raw_frame.f_lasti - 4
        )
        self.raw_frame.f_trace_opcodes = True
        self.raw_frame.f_trace = self.local_tracer
        sys.settrace(self.global_tracer)

    def stop(self):
        if not self.frame_logger or self.tracer_state == TracerFSM.CALLED:
            # No frame_logger means start() did not run.
            return

        self.tracer_state = TracerFSM.next_state(self.tracer_state, TracerFSM.STOP)
        sys.settrace(None)

        # self.global_frame is set means tracer.start() was called explicitly.
        # Otherwise the @trace decorator is used.
        if self.raw_frame:
            self.raw_frame.f_trace = None
            del self.raw_frame
            # Checks the value stack is in correct state: no extra elements left on
            # stack.These two are tracers replaced with placeholders.
            assert self.frame_logger.frame.value_stack.stack == [[], []]
        else:
            assert len(self.frame_logger.frame.value_stack.stack) == 0

        # If run in production, let the server wait for termination.
        if not utils.run_in_test():
            self._wait_for_termination()

    def _wait_for_termination(self):
        """
        RPC server should keep running until explicitly terminated, but it should not
        block the execution of user code. Thus we let it wait in a separate thread.
        """
        from threading import Thread

        Thread(target=self.server.wait_for_termination).start()

    def __call__(self, disabled: Union[Union[FunctionType, MethodType], bool] = False):
        """Enables the tracer object to be used as a decorator.

        Note that the decorator can take a `disabled` argument, or no argument:

            @tracer(disabled=True)
            def f():
        or
            @tracer
            def f():

        To achieve this, the `disabled` parameter can either be a boolean, or the
        decorated function. To match the semantics, a better name for the parameter is
        "function_or_disabled", but users being able to write `disabled=True` is a
        must-have feature, therefore we have no choice but to name it "disabled".

        This is ugly and I hope to find a way to change it. singledispatch[method] won't
        work, because it does not take keyword arguments. TypeDispatch from fastcore
        (https://fastcore.fast.ai/dispatch.html) is similar to singledispatch, but it's
        not ideal either as it requires putting method implementation outside of class.
        """

        def decorator(f, disabled_by_user=False):
            @functools.wraps(f)
            def wrapper(*args, **kwargs):
                # TracerFSM.ACTIVE: appeared in recursive call. The tracer has been
                #   activated in the outer call frame.
                # TracerFSM.CALLED: call the function multiple times.
                # In both cases, don't enable tracing.
                if disabled_by_user or self.tracer_state in {
                    TracerFSM.ACTIVE,
                    TracerFSM.CALLED,
                }:
                    return f(*args, **kwargs)

                self.decorated_function_code_id = id(f.__code__)
                sys.settrace(self.global_tracer)
                result = f(*args, **kwargs)
                self.stop()
                return result

            return wrapper

        if type(disabled) == bool:
            return functools.partial(decorator, disabled_by_user=disabled)
        else:
            decorated_function = disabled
            return decorator(decorated_function)

    @property
    def events(self):
        return self.frame_logger.frame.events

    @property
    def loops(self):
        """Test only. Provides access to logged events."""
        return list(self.frame_logger.frame.loops.values())

    @property
    def global_tracer(self):
        def _global_tracer(raw_frame, event, arg):
            # Later when we need to trace more functions, we should identify those
            # functions or at least use utils.should_exclude(frame) to avoid tracing
            # unnecessary frames.
            #
            # self.tracer_state == TracerFSM.INITIAL is for preventing stepping into
            # recursive calls, since their f_code are the same.
            if (
                event == "call"
                and id(raw_frame.f_code) == self.decorated_function_code_id
                and self.tracer_state == TracerFSM.INITIAL
            ):
                raw_frame.f_trace_opcodes = True
                self._initialize_frame_and_logger(raw_frame, initial_instr_pointer=0)
                return self.local_tracer

        return _global_tracer

    @property
    def local_tracer(self):
        def _local_tracer(raw_frame, event, arg):
            if utils.should_exclude(raw_frame):
                return
            if event == "opcode":
                self.frame_logger.update(raw_frame)
            if event == "return":
                # print(raw_frame, event, arg, raw_frame.f_lasti)
                self.frame.log_return_event(raw_frame, value=arg)

        return _local_tracer
