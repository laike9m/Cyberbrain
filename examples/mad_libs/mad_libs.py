import os
import sys

from cyberbrain import trace


@trace
def main(file, inputs):
    text = file.read().rstrip()
    had_placeholders = False
    tmpl = "Give me {} {}: "

    while True:
        brackets = find_brackets(text)
        if not brackets:
            break

        start, stop = brackets
        placeholder = text[start : stop + 1]
        pos = placeholder[1:-1]
        article = "an" if pos.lower()[0] in "aeiou" else "a"
        answer = inputs.pop(0) if inputs else input(tmpl.format(article, pos))
        text = text[0:start] + answer + text[stop + 1 :]
        had_placeholders = True

    if had_placeholders:
        print(text)
    else:
        sys.exit(f'"{args.file.name}" has no placeholders.')


def find_brackets(text):
    """Find angle brackets"""

    start = text.index("<") if "<" in text else -1
    stop = text.index(">") if start >= 0 and ">" in text[start + 2 :] else -1
    return (start, stop) if start >= 0 and stop >= 0 else None


if __name__ == "__main__":
    os.chdir(os.path.dirname(__file__))
    main(
        file=open("romeo_juliet.txt", "rt"),
        inputs=[
            "cars",
            "Detroit",
            "oil",
            "pistons",
            "stick shift",
            "furious",
            "accelerate",
            "42",
            "foot",
            "hammer",
        ],
    )
