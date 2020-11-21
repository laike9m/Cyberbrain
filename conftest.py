import sys

# test_outside_func.py is ignored because it has code in global scope, and is always
# executed if not ignored.
collect_ignore = [
    "test/test_outside_func.py",
    "test/test_assert_raise.py",
    "test/test_exception.py",
]

if sys.version_info[:2] < (3, 8):
    collect_ignore.append("test/test_block_py38.py")
