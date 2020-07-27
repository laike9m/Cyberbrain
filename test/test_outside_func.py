"""Certain instructions can only be tested outside of a function."""

from cyberbrain import Tracer, InitialValue, Deletion, Mutation, Symbol
from utils import assert_GetFrame

tracer = Tracer()

x = 1

tracer.start_tracing()
del x  # DELETE_NAME
y: int
tracer.stop_tracing()


def test_module(rpc_stub):
    assert tracer.events == {
        "x": [
            InitialValue(target=Symbol("x"), value=1, lineno=11),
            Deletion(target=Symbol("x"), lineno=11),
        ],
        "__annotations__": [
            InitialValue(target=Symbol("__annotations__"), value={}, lineno=12),
            Mutation(
                target=Symbol("__annotations__"),
                value={"y": int},
                sources=set(),  # `int` is a built-in so is excluded from sources.
                lineno=12,
            ),
        ],
    }

    assert_GetFrame(rpc_stub, "test_outside_func")
