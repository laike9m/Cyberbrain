from cyberbrain import tracer


def hello():
    tracer.start()
    x = "hello"
    y = x + " world"
    x, y = y, x
    tracer.stop()


if __name__ == "__main__":
    hello()
