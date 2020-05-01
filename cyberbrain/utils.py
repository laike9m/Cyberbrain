"""Utility functions."""

import inspect
import os
import sysconfig
from pprint import pformat

from pygments import highlight
from pygments.formatters import Terminal256Formatter
from pygments.lexers import PythonLexer

_INSTALLATION_PATHS = list(sysconfig.get_paths().values())


def is_exception(obj) -> bool:
    """Checks whether the given obj is an exception instance or class."""
    if isinstance(obj, BaseException):
        return True

    return is_exception_class(obj)


def is_exception_class(obj) -> bool:
    """Checks whether the given obj is an exception class."""
    return inspect.isclass(obj) and issubclass(obj, BaseException)


def should_exclude(frame):
    """Determines whether we should log events from file.

    As of now, we exclude files from installation path, which usually means:
    .../3.7.1/lib/python3.7
    .../3.7.1/include/python3.7m
    .../lib/python3.7/site-packages

    Also we exclude frozen modules, as well as some weird cases.
    """

    filename = frame.f_code.co_filename

    # Exclude 'call' event of "tracer.init/register()", so that the execution of
    # these methods will never be traced.
    if filename.endswith(os.path.join("cyberbrain", "api.py")):
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
