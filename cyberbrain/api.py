"""Cyberbrain public API and tracer setup."""

import argparse
import sys

from . import logger, utils
# from .rpc import server
from .basis import _dummy

_debug_mode = False

# This is to allow using debug mode in both test and non-test code.
# Flag will conflict, so only execute it if not running a test.
if "pytest" not in sys.modules:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--debug_mode",
        dest="debug_mode",
        action="store_true",
        help="Whether to log more stuff for debugging.",
    )
    parser.set_defaults(debug_mode=False)
    args, _ = parser.parse_known_args()
    _debug_mode = args.debug_mode


class Tracer:
    def __init__(self, debug_mode=_debug_mode):
        self.global_frame = None
        self.frame = None
        self.debug_mode = debug_mode

    def init(self):
        """Initializes tracing."""
        self.global_frame = sys._getframe(1)
        self.frame = logger.FrameLogger(self.global_frame, debug_mode=self.debug_mode)
        self.global_frame.f_trace_opcodes = True
        self.global_frame.f_trace = self.local_tracer
        sys.settrace(self.global_tracer)

    def register(self, target=_dummy):
        # Checks the value stack is in correct state: no extra elements left on stack.
        assert self.frame.value_stack.stack == [["tracer"], ["tracer"]]
        sys.settrace(None)
        self.global_frame.f_trace = None
        del self.global_frame
        # if "pytest" not in sys.modules:
        #     server.run()

    @property
    def events(self):
        """Test only. Provide access to logged events."""
        return self.frame.frame_state.accumulated_events

    @property
    def global_tracer(self):
        def _global_tracer(frame, event, arg):
            if utils.should_exclude(frame):
                return
            frame.f_trace_opcodes = True
            # print(frame, event, arg)
            return self.local_tracer

        return _global_tracer

    @property
    def local_tracer(self):
        def _local_tracer(frame, event, arg):
            if utils.should_exclude(frame):
                return
            if event == "opcode":
                # print(frame, event, arg)
                self.frame.update(frame)

        return _local_tracer
