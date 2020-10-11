#!/usr/bin/env python3
"""Password maker, https://xkcd.com/936/"""

import argparse
import random
import re
import string

from cyberbrain import trace


# --------------------------------------------------
def get_args():
    """Get command-line arguments"""

    parser = argparse.ArgumentParser(
        description="Password maker",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "file",
        metavar="FILE",
        type=argparse.FileType("rt"),
        nargs="+",
        help="Input file(s)",
    )

    parser.add_argument(
        "-n",
        "--num",
        metavar="num_passwords",
        type=int,
        default=3,
        help="Number of passwords to generate",
    )

    parser.add_argument(
        "-w",
        "--num_words",
        metavar="num_words",
        type=int,
        default=4,
        help="Number of words to use for password",
    )

    parser.add_argument(
        "-m",
        "--min_word_len",
        metavar="minimum",
        type=int,
        default=3,
        help="Minimum word length",
    )

    parser.add_argument(
        "-x",
        "--max_word_len",
        metavar="maximum",
        type=int,
        default=6,
        help="Maximum word length",
    )

    parser.add_argument("-s", "--seed", metavar="seed", type=int, help="Random seed")

    parser.add_argument("-l", "--l33t", action="store_true", help="Obfuscate letters")

    return parser.parse_args()


@trace
def main():
    args = get_args()
    random.seed(args.seed)  # <1>
    words = set()

    def word_len(word):
        return args.min_word_len <= len(word) <= args.max_word_len

    for fh in args.file:
        for line in fh:
            for word in filter(word_len, map(clean, line.lower().split())):
                words.add(word.title())

    words = sorted(words)
    passwords = ["".join(random.sample(words, args.num_words)) for _ in range(args.num)]

    if args.l33t:
        passwords = map(l33t, passwords)

    print("\n".join(passwords))


def clean(word):
    """Remove non-word characters from word"""

    return re.sub("[^a-zA-Z]", "", word)


def l33t(text):
    """l33t"""

    text = ransom(text)
    xform = str.maketrans(
        {"a": "@", "A": "4", "O": "0", "t": "+", "E": "3", "I": "1", "S": "5"}
    )
    return text.translate(xform) + random.choice(string.punctuation)


def ransom(text):
    """Randomly choose an upper or lowercase letter to return"""

    return "".join(
        map(lambda c: c.upper() if random.choice([0, 1]) else c.lower(), text)
    )


if __name__ == "__main__":
    main()
