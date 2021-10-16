import pkg_resources
import sys

# test_outside_func.py is ignored because it has code in global scope, and is always
# executed if not ignored.
collect_ignore = [
    "test/test_outside_func.py",
]

_python_version = sys.version_info[:2]

if _python_version == (3, 7):
    collect_ignore.append("test/test_block_py38.py")

if _python_version == (3, 10):
    collect_ignore.append("test/test_generator.py")

installed = {pkg.key for pkg in pkg_resources.working_set}

for pkg in ("numpy", "pandas"):
    if pkg not in installed:
        collect_ignore.append(f"test/test_{pkg}.py")
