"""Utility functions."""

from __future__ import annotations

import collections
import dis
import inspect
import os
import subprocess
import sys
import sysconfig
from copy import deepcopy
from functools import lru_cache
from pathlib import Path
from pprint import pformat
from types import FrameType
from typing import Any, Optional

import jsonpickle
from pygments import highlight
from pygments.formatters import Terminal256Formatter
from pygments.lexers import PythonLexer

_INSTALLATION_PATHS = list(sysconfig.get_paths().values())
_PYTHON_EXECUTABLE_PATH = sys.executable


def should_ignore_event(
    *, target: str, value: Any, frame: Optional[FrameType] = None
) -> bool:
    """Determines whether we should ignore this event."""
    from .tracer import Tracer

    # Excludes events from tracer.
    if isinstance(value, Tracer):
        return True

    # Excludes events from modules.
    if inspect.ismodule(value):
        return True

    # Excludes events from builtins.
    if frame and target in frame.f_builtins:
        return True

    return False


def map_bytecode_offset_to_lineno(frame: FrameType) -> dict[int, int]:
    """Maps bytecode offset to lineno in file.

    Note that the lineno may not be accurate for multi-line statements. If we find
    this to be blocking, we might need to use a Range to represent lineno.
    """
    mapping = dict(dis.findlinestarts(frame.f_code))
    frame_byte_count = len(frame.f_code.co_code)
    for offset, lineno in mapping.copy().items():
        while offset <= frame_byte_count:
            offset += 2
            if offset in mapping:
                break
            mapping[offset] = lineno

    return mapping


def get_jump_target_or_none(instr: dis.Instruction) -> Optional[int]:
    if instr.opcode in dis.hasjrel:
        return instr.offset + 2 + instr.arg
    elif instr.opcode in dis.hasjabs:
        return instr.arg


def to_json(python_object: Any):
    # TODO: Once we implemented better deserialization in Js, use unpicklable=True.
    return jsonpickle.encode(python_object, unpicklable=False)


@lru_cache(maxsize=1)
def run_in_test() -> bool:
    return "pytest" in sys.modules


def computed_gotos_enabled() -> bool:
    script_path = os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        "internal",
        "_detect_computed_goto.py",
    )
    stdout, _ = subprocess.Popen(
        [_PYTHON_EXECUTABLE_PATH, script_path], stdout=subprocess.PIPE
    ).communicate()

    return stdout == b"True"


def flatten(*args: any) -> list:
    """Flattens the given series of inputs, accepts list or non-list."""
    result = []
    for arg in args:
        if isinstance(arg, collections.abc.Iterable):
            for elem in arg:
                result.append(elem)
        else:
            result.append(arg)

    return result


def is_exception(obj) -> bool:
    """Checks whether the given obj is an exception instance or class."""
    if isinstance(obj, BaseException):
        return True

    return is_exception_class(obj)


def is_exception_class(obj) -> bool:
    """Checks whether the given obj is an exception class."""
    return inspect.isclass(obj) and issubclass(obj, BaseException)


def should_exclude(frame):
    """Determines whether we should log events from this frame.

    As of now, we exclude files from installation path, which usually means:
    .../3.7.1/lib/python3.7
    .../3.7.1/include/python3.7m
    .../lib/python3.7/site-packages

    Also we exclude frozen modules, as well as some weird cases.
    """

    filename = frame.f_code.co_filename

    # Exclude 'call' event of "tracer.init/register()", so that the execution of
    # these methods will never be traced.
    if filename.endswith(os.path.join("cyberbrain", "tracer.py")):
        return True

    if any(filename.startswith(path) for path in _INSTALLATION_PATHS):
        return True

    if any(
        name in filename
        for name in (
            "importlib._bootstrap",
            "importlib._bootstrap_external",
            "zipimport",
            "<string>",  # Dynamically generated frames
        )
    ):
        return True

    return False


def pprint(*args):
    output = ""
    for arg in args:
        if isinstance(arg, str):
            output += arg + "\n"
        else:
            # Outputs syntax-highlighted object. See
            # https://gist.github.com/EdwardBetts/0814484fdf7bbf808f6f
            output += (
                highlight(pformat(arg), PythonLexer(), Terminal256Formatter()) + "\n"
            )
    print(output)


def deepcopy_value_from_frame(name: str, frame: FrameType):
    """Given a frame and a name(identifier) saw in this frame, returns its value.

    The value has to be deep copied to avoid being changed by code coming later.

    I'm not 100% sure if this will always return the correct value. If we find a
    case where it returns the wrong value due to name collisions, we can modify
    code and store names with their scopes, like (a, local), (b, global).

    Once we have a frame class, we might move this method there.
    """
    value = get_value_from_frame(name, frame)

    # There are certain things you can't copy, like module.
    try:
        return deepcopy(value)
    except TypeError:
        return repr(value)


def get_value_from_frame(name: str, frame: FrameType):
    assert name_exist_in_frame(name, frame)
    if name in frame.f_locals:
        value = frame.f_locals[name]
    elif name in frame.f_globals:
        value = frame.f_globals[name]
    else:
        value = frame.f_builtins[name]
    return value


def name_exist_in_frame(name: str, frame: FrameType) -> bool:
    return any(
        [name in frame.f_locals, name in frame.f_globals, name in frame.f_builtins]
    )


def shorten_path(file_path, length):
    """
    Split the path into separate parts, select the last 'length' elements and join them
    """
    return str(Path(*Path(file_path).parts[-length:]))


if __name__ == "__main__":
    # For development.
    print(computed_gotos_enabled())
