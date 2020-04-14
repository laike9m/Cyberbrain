"""Certain instructions can only be tested outside of a function."""

from cyberbrain import Tracer

tracer = Tracer()

x = 1

tracer.init()
del x
tracer.register()


def test_delete_name():
    assert tracer.logger.changes == [{"target": "x"}]
