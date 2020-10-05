from cyberbrain import trace


def main():
    x = 1

    class A:
        pass

    @trace
    def use_nonlocal():
        nonlocal x
        x = 10
        a = A()

    use_nonlocal()


if __name__ == "__main__":
    main()
