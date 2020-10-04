"""Make rhyming words"""

import re
import string

from cyberbrain import trace


@trace
def stemmer(word):
    """Return leading consonants (if any), and 'stem' of word"""

    word = word.lower()
    vowels = "aeiou"
    consonants = "".join([c for c in string.ascii_lowercase if c not in vowels])
    pattern = (
        "([" + consonants + "]+)?"  # capture one or more, optional
        "([" + vowels + "])"  # capture at least one vowel
        "(.*)"  # capture zero or more of anything
    )

    match = re.match(pattern, word)
    if match:
        p1 = match.group(1) or ""
        p2 = match.group(2) or ""
        p3 = match.group(3) or ""
        return p1, p2 + p3
    else:
        return word, ""


if __name__ == "__main__":
    stemmer("apple")
