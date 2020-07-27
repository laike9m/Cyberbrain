import time

from cyberbrain import Tracer


def hello():
    tracer = Tracer()
    tracer.start_tracing()
    time.sleep(5)
    print("hello world")
    tracer.stop_tracing()


if __name__ == "__main__":
    hello()
