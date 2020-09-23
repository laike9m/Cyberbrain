#!/usr/bin/env python3
"""Bottles of beer song"""

from cyberbrain import trace


def main():
    """Make a jazz noise here"""

    print("\n\n".join(map(verse, range(3, 0, -1))))


@trace
def verse(bottle):
    """Sing a verse"""

    next_bottle = bottle - 1
    s1 = "" if bottle == 1 else "s"
    s2 = "" if next_bottle == 1 else "s"
    num_next = "No more" if next_bottle == 0 else next_bottle
    return "\n".join(
        [
            f"{bottle} bottle{s1} of beer on the wall,",
            f"{bottle} bottle{s1} of beer,",
            f"Take one down, pass it around,",
            f"{num_next} bottle{s2} of beer on the wall!",
        ]
    )


# --------------------------------------------------
if __name__ == "__main__":
    main()
