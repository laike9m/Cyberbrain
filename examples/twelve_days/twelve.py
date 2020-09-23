#!/usr/bin/env python3
"""Twelve Days of Christmas"""


from cyberbrain import trace


def main():
    verses = list(map(verse, range(1, 13)))
    print(verses)


@trace
def verse(day):
    """Create a verse"""

    ordinal = [
        "first",
        "second",
        "third",
        "fourth",
        "fifth",
        "sixth",
        "seventh",
        "eighth",
        "ninth",
        "tenth",
        "eleventh",
        "twelfth",
    ]

    gifts = [
        "A partridge in a pear tree.",
        "Two turtle doves,",
        "Three French hens,",
        "Four calling birds,",
        "Five gold rings,",
        "Six geese a laying,",
        "Seven swans a swimming,",
        "Eight maids a milking,",
        "Nine ladies dancing,",
        "Ten lords a leaping,",
        "Eleven pipers piping,",
        "Twelve drummers drumming,",
    ]

    lines = [f"On the {ordinal[day - 1]} day of Christmas,", "My true love gave to me,"]

    lines.extend(reversed(gifts[:day]))

    if day > 1:
        lines[-1] = "And " + lines[-1].lower()

    return "\n".join(lines)


if __name__ == "__main__":
    main()
