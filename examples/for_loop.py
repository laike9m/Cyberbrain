from cyberbrain import trace


@trace
def one_loop():
    for i in range(5):
        a = i
        b = a


if __name__ == "__main__":
    one_loop()