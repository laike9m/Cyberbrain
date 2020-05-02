import sys

collect_ignore = []

if sys.version_info[:2] < (3, 8):
    collect_ignore.append("test/test_block_py38.py")
