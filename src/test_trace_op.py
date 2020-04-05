"""
Set trace on opcode level.
"""

import dis
import sys
import inspect
import sysconfig
from functools import lru_cache

import execution_log

paths = list(sysconfig.get_paths().values())

_current_frame = sys._getframe()

# Right now there's only a single frame(global). We should create an logger for each frame.
execution_logger = execution_log.Logger(frame=_current_frame)


@lru_cache()
def should_exclude(filename):
    if "importlib" in filename:
        return True
    for path in paths:
        if filename.startswith(path):
            return True
    return False


def printer_global(frame, event, arg):
    if should_exclude(frame.f_code.co_filename):
        return
    frame.f_trace_opcodes = True
    # print(frame, event, arg)
    return printer_local


def printer_local(frame, event, arg):
    if should_exclude(frame.f_code.co_filename):
        return
    if event == "opcode":
        # print(frame, event, arg, frame.f_lasti)
        execution_logger.detect_chanages(frame.f_lasti)


sys.settrace(printer_global)
_current_frame.f_trace = printer_local
_current_frame.f_trace_opcodes = True


# class A:
#     pass
#
#
# o = A()
# x = 0
# for i in range(1, 3):
#     o.value = i
#     x = i

a = []
if a:
    x = 1
else:
    x = 2

print("the end")
