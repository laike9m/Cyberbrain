"""Utility functions."""

from __future__ import annotations

import dis
import inspect
import os
import re
import subprocess
import sys
import sysconfig
from functools import lru_cache
from pathlib import Path
from pprint import pformat
from types import FrameType
from typing import Any, Optional

import jsonpickle
import more_itertools
from cheap_repr import cheap_repr
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
    json = jsonpickle.encode(python_object, unpicklable=False)
    if json == "null" and python_object is not None:
        return '{"repr": "%s"}' % get_repr(python_object)
    else:
        return json


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


def is_exception(obj) -> bool:
    """Checks whether the given obj is an exception instance or class."""
    return isinstance(obj, BaseException) or is_exception_class(obj)


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


def flatten(*args: any) -> list:
    """Flattens the given series of inputs, accepts nested list or non-list."""
    return list(more_itertools.collapse(args))


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


def get_repr(obj: Any) -> str:
    """Returns a short repr text of the given object.

    It uses cheap_repr (https://github.com/alexmojaki/cheap_repr) to get a short and
    optimized repr text, but that's not enough. For objects, the repr look like:
    "<test_attribute.foo>.A object at 0x10cd41700>"
    of which the address " at 0x10cd41700" part is a bit redundant (considering the
    limited space in the trace graph). So we'll remove the address part if it exists.
    """

    # String is different, because we need to display the quotes in the tooltip, so
    # adding a pair of extra quote.
    if type(obj) == str:
        return f'"{obj}"'

    repr_text = cheap_repr(obj)
    match = re.search("at 0x", repr_text)
    if not match:
        return repr_text
    else:
        repr_text = repr_text[: match.start(0) - 1]
        # Sometimes repr_text is like "<function f", add a '>' at the end.
        if repr_text.startswith("<") and not repr_text.endswith(">"):
            return repr_text + ">"


def shorten_path(file_path, length):
    """
    Split the path into separate parts, select the last 'length' elements and join them
    """
    return str(Path(*Path(file_path).parts[-length:]))


if __name__ == "__main__":
    # For development.
    print(computed_gotos_enabled())
