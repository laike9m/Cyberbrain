#!/usr/bin/env python3
"""Emulate wc (word count)"""

import argparse
import sys

from cyberbrain import tracer


# --------------------------------------------------
def get_args():
    """Get command-line arguments"""

    parser = argparse.ArgumentParser(
        description="Emulate wc (word count)",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "file",
        metavar="FILE",
        nargs="*",
        default=[sys.stdin],
        type=argparse.FileType("rt"),
        help="Input file(s)",
    )

    return parser.parse_args()


# TODO: Problems:
#   1. Trace graph is not compact enough
#   2. The inner loop and symbol "line" is not tracked

# --------------------------------------------------
@tracer
def main():
    """Make a jazz noise here"""

    args = get_args()

    total_lines, total_bytes, total_words = 0, 0, 0
    for fh in args.file:
        num_lines, num_words, num_bytes = 0, 0, 0
        for line in fh:
            num_lines += 1
            num_bytes += len(line)
            num_words += len(line.split())

        total_lines += num_lines
        total_bytes += num_bytes
        total_words += num_words

        print(f"{num_lines:8}{num_words:8}{num_bytes:8} {fh.name}")

    if len(args.file) > 1:
        print(f"{total_lines:8}{total_words:8}{total_bytes:8} total")


# --------------------------------------------------
if __name__ == "__main__":
    main()
