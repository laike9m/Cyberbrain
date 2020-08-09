from cyberbrain import Tracer


def hello():
    tracer = Tracer()
    tracer.start_tracing()
    x = "hello"
    y = x + " world"
    x, y = y, x
    tracer.stop_tracing()


if __name__ == "__main__":
    hello()
