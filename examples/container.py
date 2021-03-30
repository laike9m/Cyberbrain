from cyberbrain import trace


@trace
def container():
    return list(range(1000))


if __name__ == "__main__":
    container()
