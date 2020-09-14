"""Cyberbrain public API and tracer setup."""

import argparse
import functools
import sys
from types import MethodType, FunctionType
from typing import Optional, Union

from get_port import get_port

from . import logger, utils, rpc_server

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


class Tracer:

    debug_mode = _debug_mode

    def __init__(self, debug_mode=None):
        self.disabled = False
        self.global_frame = None
        self.decorated_function_code_id = None
        self.frame_logger: Optional[logger.BaseFrameLogger] = None
        if debug_mode is not None:
            self.debug_mode = debug_mode

        # For now server is put inside Tracer. Later when we need to trace multiple
        # frames it should be moved to somewhere else.
        self.server = rpc_server.Server()
        if utils.run_in_test():
            # Picks a random port for testing to allow concurrent test execution.
            self.server.serve(port=get_port())
        else:
            self.server.serve()

    def start(self, disabled=False):
        """Initializes tracing."""
        if disabled:
            self.disabled = True
            return

        self.global_frame = sys._getframe(1)
        self.frame_logger = logger.FrameLoggerForExplicitTracer(
            self.global_frame, debug_mode=self.debug_mode
        )
        self.global_frame.f_trace_opcodes = True
        self.global_frame.f_trace = self.local_tracer
        sys.settrace(self.global_tracer)

    def stop(self):
        if self.disabled:
            return

        sys.settrace(None)
        self.global_frame.f_trace = None
        del self.global_frame
        # Checks the value stack is in correct state: no extra elements left on stack.
        # These two are tracers replaced with placeholders.
        assert self.frame_logger.frame.value_stack.stack == [[], []]
        if not utils.run_in_test():
            # If run in production, let the server wait for termination.
            self.server.wait_for_termination()

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
        not ideal either as it requires to put method implementation outside of class.
        """

        def decorator(f):
            @functools.wraps(f)
            def wrapper(*args, **kwargs):
                if not self.disabled:
                    self.decorated_function_code_id = id(f.__code__)
                    sys.settrace(self.global_tracer)
                result = f(*args, **kwargs)
                sys.settrace(None)
                return result

            return wrapper

        if type(disabled) == bool:
            self.disabled = disabled
            return decorator
        else:
            decorated_function = disabled
            return decorator(decorated_function)

    @property
    def events(self):
        return self.frame_logger.frame.accumulated_events

    @property
    def loops(self):
        """Test only. Provides access to logged events."""
        return list(self.frame_logger.frame.loops.values())

    @property
    def global_tracer(self):
        def _global_tracer(frame, event, arg):
            # Later when we need to trace more functions, we should identify those
            # functions or at least use utils.should_exclude(frame) to avoid tracing
            # unnecessary frames.
            if event == "call" and id(frame.f_code) == self.decorated_function_code_id:
                frame.f_trace_opcodes = True
                self.frame_logger = logger.FrameLoggerForDecorator(
                    frame, debug_mode=self.debug_mode
                )
                return self.local_tracer

        return _global_tracer

    @property
    def local_tracer(self):
        def _local_tracer(frame, event, arg):
            if utils.should_exclude(frame):
                return
            if event == "opcode":
                # print(frame, event, arg)
                self.frame_logger.update(frame)

        return _local_tracer
