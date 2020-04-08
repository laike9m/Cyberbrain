"""Utility functions."""

import inspect
import os
import sysconfig

from functools import lru_cache


_INSTALLATION_PATHS = list(sysconfig.get_paths().values())


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
            "importlib._boostrap",
            "importlib._bootstrap_external",
            "zipimport",
            "<string>",  # Dynamically generated frames
        )
    ):
        return True

    return False
