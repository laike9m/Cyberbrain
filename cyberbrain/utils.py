"""Utility functions."""

from __future__ import annotations

import dis
import sysconfig

import argparse
import cheap_repr
import gc
import inspect
import jsonpickle
import more_itertools
import os
import re
import subprocess
import sys
from functools import lru_cache
from pathlib import Path
from pprint import pformat
from pygments import highlight
from pygments.formatters import Terminal256Formatter
from pygments.lexers import PythonLexer
from types import FrameType
from typing import Any, Optional, Set

from . import basis, tracer

# These pickle handlers rely on Numpy and Pandas, so it only makes sense to register
# them if Numpy or Pandas are installed.
try:
    import jsonpickle.ext.numpy as jsonpickle_numpy

    # Make sure Numpy and Pandas objects can be correctly encoded.
    # https://github.com/jsonpickle/jsonpickle#numpy-support
    jsonpickle_numpy.register_handlers()
except (ImportError, RuntimeError):
    pass

try:
    import jsonpickle.ext.pandas as jsonpickle_pandas

    jsonpickle_pandas.register_handlers()
except (ImportError, RuntimeError):
    pass

_INSTALLATION_PATHS = list(sysconfig.get_paths().values())
_PYTHON_EXECUTABLE_PATH = sys.executable

jsonpickle.set_preferred_backend("ujson")


# To not let it show warnings
@cheap_repr.register_repr(argparse.Namespace)
def repr_for_namespace(_, __):
    return "argparse.Namespace"


def get_current_callable(frame: FrameType):
    """Returns the callable that generates the frame.

    See https://stackoverflow.com/a/52762678/2142577.
    """
    return [
        obj
        for obj in gc.get_referrers(frame.f_code)
        if hasattr(obj, "__code__") and obj.__code__ is frame.f_code
    ][0]


def get_parameters(frame: FrameType) -> Set[str]:
    """Get the parameters' names from a frame.

    e.g. f(a, b, *args, **kwargs)
    If called with f(1, 2, 3, x=1), returns {'a', 'b', 'args', 'kwargs'}.
    """
    arg_info = inspect.getargvalues(frame)
    parameters = set(arg_info.args)
    if arg_info.varargs is not None:
        parameters.add(arg_info.varargs)
    if arg_info.keywords is not None:
        parameters.add(arg_info.keywords)
    return parameters


def should_ignore_event(
    *, target: str, value: Any, frame: Optional[FrameType] = None
) -> bool:
    """Determines whether we should ignore this event."""

    # Excludes events from tracer.
    if isinstance(value, tracer.Tracer):
        return True

    # Excludes events from modules.
    if inspect.ismodule(value):
        return True

    # Excludes events from builtins.
    return frame and target in frame.f_builtins


def map_bytecode_offset_to_lineno(frame: FrameType) -> dict[int, int]:
    """Maps bytecode offset to lineno in source code.

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


# get_jump_target_or_none is called for every instruction, as a micro-optimization,
# we avoid checking basis.VERSION_INFO everytime by generating the correct function.
def _compute_get_jump_target_or_none():
    # bpo-27129, use instruction offsets (as opposed to byte offsets).
    bytes_per_offset = 1 if basis.VERSION_INFO < (3, 10) else 2

    def function_to_return(instr):
        if instr.opcode in dis.hasjrel:
            return instr.offset + 2 + instr.arg * bytes_per_offset
        elif instr.opcode in dis.hasjabs:
            return instr.arg * bytes_per_offset

    return function_to_return


# Returns the jump target for a jump instruction, otherwise none.
get_jump_target_or_none: Callable[
    [dis.Instruction], Optional[int]
] = _compute_get_jump_target_or_none()


def to_json(python_object: Any):
    # TODO: Once we implemented better deserialization in Js, use unpicklable=True.
    try:
        if (
            hasattr(python_object, "__iter__")
            and hasattr(python_object, "__next__")
            and iter(python_object) == python_object
        ):
            raise Exception("Cannot encode iterators")
        json = jsonpickle.encode(python_object, unpicklable=False)
    except:
        # There are always things we just cannot encode, like a ML model.
        # In this case, use its repr.
        return '{"repr": "%s"}' % get_repr(python_object)

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

    # Exclude 'call' event of "tracer.start/end()", so that the execution of
    # these methods will never be traced.
    if filename.endswith(os.path.join("cyberbrain", "tracer.py")):
        return True

    if any(filename.startswith(path) for path in _INSTALLATION_PATHS):
        return True

    return any(
        name in filename
        for name in (
            "importlib._bootstrap",
            "importlib._bootstrap_external",
            "zipimport",
            "<string>",  # Dynamically generated frames
        )
    )


def flatten(*args: any) -> list:
    """Flattens the given series of inputs, accepts nested list or non-list."""
    return list(more_itertools.collapse(args))


def pprint(*args):
    output = "".join(
        arg + "\n"
        if isinstance(arg, str)
        else (
            # Outputs syntax-highlighted object. See
            # https://gist.github.com/EdwardBetts/0814484fdf7bbf808f6f
            highlight(pformat(arg), PythonLexer(), Terminal256Formatter())
            + "\n"
        )
        for arg in args
    )
    print(output)


def get_value_from_frame(name: str, frame: FrameType):
    assert name_exist_in_frame(name, frame)
    if name in frame.f_locals:
        return frame.f_locals[name]
    elif name in frame.f_globals:
        return frame.f_globals[name]
    else:
        return frame.f_builtins[name]


# TODO: we can use a id(frame) -> name cache.
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

    repr_text = cheap_repr.cheap_repr(obj)
    match = re.search("at 0x", repr_text)
    if not match:
        return repr_text
    repr_text = repr_text[: match.start(0) - 1]
    # Sometimes repr_text is like "<function f", add a '>' at the end.
    if repr_text.startswith("<") and not repr_text.endswith(">"):
        return repr_text + ">"


def shorten_path(file_path, length):
    """
    Split the path into separate parts, select the last 'length' elements and join them
    """
    return str(Path(*Path(file_path).parts[-length:]))


def all_none(*args):
    return all(arg is None for arg in args)


if __name__ == "__main__":
    # For development.
    print(computed_gotos_enabled())
