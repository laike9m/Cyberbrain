import msgpack
import re


def test_repr(tracer, check_golden_file):
    class A:
        pass

    tracer.start()
    match = re.match("foo", "foobar")
    a = A()
    tracer.stop()
