from cyberbrain import trace


def main():
    x = 1

    @trace
    def use_nonlocal():
        nonlocal x
        x = 10

    use_nonlocal()


if __name__ == "__main__":
    main()
