import sys
import importlib

# test_outside_func.py is ignored because it has code in global scope, and is always
# executed if not ignored.
collect_ignore = [
    "test/test_outside_func.py",
]

_python_version = sys.version_info[:2]

if _python_version == (3, 7):
    collect_ignore.append("test/test_block_py38.py")
    collect_ignore.append("test/test_walrus.py")

for pkg in ("numpy", "pandas"):
    try:
        importlib.import_module(pkg)
    except ImportError:
        collect_ignore.append(f"test/test_{pkg}.py")
