from __future__ import annotations

import sys
from functools import lru_cache

import detect


@lru_cache(maxsize=1)
def get_os_type() -> str:
    if detect.linux:
        return "linux"
    if detect.windows:
        return "windows"
    if detect.mac:
        return "mac"
    return "other"


python_version = {(3, 7): "py37", (3, 8): "py38", (3, 9): "py39"}[sys.version_info[:2]]
os_type = get_os_type()


def get_value(value_dict: dict[str, any]):
    """
    Accept an argument like {'py37': 1, 'py38': 2},
    or {"windows": 1, "linux": 2, "mac": 3}

    Used for version-dependent and OS tests.
    """
    if python_version in value_dict:
        return value_dict[python_version]
    elif os_type in value_dict:
        return value_dict[os_type]
    else:
        return value_dict["default"]
