"""Certain instructions can only be tested outside of a function."""

from cyberbrain import tracer, InitialValue, Deletion, Mutation, Symbol

x = 1

tracer.start()
del x  # DELETE_NAME
y: int
try:
    from xxx import *
except ImportError:
    pass

try:
    del aaa
except NameError:
    pass
tracer.stop()


def test_module(check_tracer_events):
    pass
