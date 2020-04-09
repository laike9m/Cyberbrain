"""Cyberbrain public API and tracer setup."""

import dis
import sys
import inspect
import sysconfig
from functools import lru_cache
from functools import partial


from . import execution_log, utils
from .basis import _dummy


class Tracer:
    def __init__(self):
        self.global_frame = None
        self.logger = None

    def init(self):
        """Initializes tracing."""
        self.global_frame = sys._getframe(1)
        self.logger = execution_log.create_logger(self.global_frame)
        self.global_frame.f_trace_opcodes = True
        self.global_frame.f_trace = self.local_tracer
        sys.settrace(self.global_tracer)

    def register(self, target=_dummy):
        sys.settrace(None)
        self.global_frame.f_trace = None
        del self.global_frame

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
                self.logger.detect_chanages(frame)

        return _local_tracer
