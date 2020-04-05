"""Cyberbrain public API and tracer setup."""

import dis
import sys
import inspect
import sysconfig
from functools import lru_cache

from . import execution_log, utils

paths = list(sysconfig.get_paths().values())

_current_frame = sys._getframe()


def global_tracer(frame, event, arg):
    if utils.should_exclude(frame.f_code.co_filename, frame.f_code.co_name):
        return
    frame.f_trace_opcodes = True
    # print(frame, event, arg)
    return local_tracer


def local_tracer(frame, event, arg):
    if utils.should_exclude(frame.f_code.co_filename):
        return
    if event == "opcode":
        # print(frame, event, arg, frame.f_lasti)
        execution_log.get_logger().detect_chanages(frame)


global_frame = None


def init():
    """Initializes tracing."""
    global global_frame

    global_frame = sys._getframe(1)
    execution_log.create_logger(global_frame)
    global_frame.f_trace_opcodes = True
    sys.settrace(global_tracer)
    global_frame.f_trace = local_tracer


_dummy = object()


def register(target=_dummy):
    sys.settrace(None)
    global_frame.f_trace = None
