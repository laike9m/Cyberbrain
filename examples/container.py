from cyberbrain import trace


@trace
def container():
    x = list(range(1000))
    return x


if __name__ == "__main__":
    container()
