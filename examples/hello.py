from cyberbrain import Tracer


def hello():
    tracer = Tracer()
    tracer.start_tracing()
    x = "hello world"
    y = x
    x, y = y, x
    tracer.stop_tracing()


if __name__ == "__main__":
    hello()
