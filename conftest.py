import pkg_resources
import sys

# test_outside_func.py is ignored because it has code in global scope, and is always
# executed if not ignored.
collect_ignore = [
    "test/test_outside_func.py",
]

if sys.version_info[:2] < (3, 8):
    collect_ignore.append("test/test_block_py38.py")

installed = {pkg.key for pkg in pkg_resources.working_set}

for pkg in ("numpy", "pandas"):
    if pkg not in installed:
        collect_ignore.append(f"test/test_{pkg}.py")
