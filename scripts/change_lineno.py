"""
This script is used to change event's expected lineno in tests.

e.g.

Original code in test_block.py:
line 9  Binding(target=Symbol("x"), value=0, lineno=7)
line 11  Binding(target=Symbol("x"), value=0, lineno=10)

We want to reduce all appeared "lineno" by 3, starting from line 10. Changed text will
be:
line 9  Binding(target=Symbol("x"), value=0, lineno=7)  # Not changed
line 11  Binding(target=Symbol("x"), value=0, lineno=7)

$ python change_lineno.py test/test_block.py
"""

import os
import re

import fire

# Assuming called from the top-level folder.
test_dir = os.path.abspath("test")


def hello(file: str, line_delta: int, start_from: int = 0):
    """Rewrite a test file's content.

    Args:
        file: the file name under the test folder, e.g. test_block
        line_delta: how we want to change expected lineno, could be negative or positive
        start_from: the line which modification should start from. Lines before
            start_from are ignored and not changed.
    """
    with open(os.path.join(test_dir, f"{file}.py"), "rt") as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        if i + 1 < start_from:
            continue
        match_obj = re.search(r"lineno=(\d+)", line)
        if not match_obj:
            continue
        new_expected_lineno = int(match_obj.group(1)) + line_delta
        line = line.replace(match_obj.group(0), f"lineno={new_expected_lineno}")
        lines[i] = line

    with open(os.path.join(test_dir, f"{file}.py"), "wt") as f:
        f.writelines(lines)


if __name__ == "__main__":
    fire.Fire(hello)
