import argparse
import random
import string

from cyberbrain import trace


@trace
def main():
    args = argparse.Namespace(
        mutations=0.6, seed=2, text="The quick brown fox jumps over the lazy dog."
    )
    text = args.text
    random.seed(args.seed)
    alpha = "".join(sorted(string.ascii_letters + string.punctuation))
    len_text = len(text)
    num_mutations = round(args.mutations * len_text)
    new_text = text

    for i in random.sample(range(len_text), num_mutations):
        new_char = random.choice(alpha.replace(new_text[i], ""))
        new_text = new_text[:i] + new_char + new_text[i + 1 :]

    print(f'You said: "{text}"\nI heard : "{new_text}"')


if __name__ == "__main__":
    main()
