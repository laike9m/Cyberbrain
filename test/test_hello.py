"""Just a hello world."""

from cyberbrain import Tracer

tracer = Tracer()


tracer.init()
x = "hello world"
y = x
tracer.register()


def test_hello():
    assert tracer.logger.mutations == [
        {"target": "x", "value": "hello world", "source": None},
        {"target": "y", "value": "hello world", "source": "x"},
    ]
