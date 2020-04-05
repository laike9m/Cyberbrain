"""Utility functions."""

import os
import sysconfig

from functools import lru_cache


_INSTALLATION_PATHS = list(sysconfig.get_paths().values())
# Used when run tests directly with pytest.
# _INSTALLATION_PATHS.append(os.path.dirname(os.path.abspath(__file__)))


@lru_cache()
def should_exclude(filename):
    """Determines whether we should log events from file.

    As of now, we exclude files from installation path, which usually means:
    .../3.7.1/lib/python3.7
    .../3.7.1/include/python3.7m
    .../lib/python3.7/site-packages

    Also we exclude frozen modules, as well as some weird cases.
    """
    if any(filename.startswith(path) for path in _INSTALLATION_PATHS) or any(
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
