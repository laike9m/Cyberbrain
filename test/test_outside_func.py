"""Certain instructions can only be tested outside of a function."""

from cyberbrain import tracer, InitialValue, Deletion, Mutation, Symbol
from utils import assert_GetFrame


x = 1

tracer.start()
del x  # DELETE_NAME
y: int
tracer.stop()


def test_module(rpc_stub):
    assert tracer.events == [
        InitialValue(target=Symbol("x"), value="1", lineno=10),
        Deletion(target=Symbol("x"), lineno=10),
        InitialValue(target=Symbol("__annotations__"), value="{}", lineno=11),
        Mutation(
            target=Symbol("__annotations__"),
            value='{"y": {"py/type": "builtins.int"}}',
            sources={
                Symbol("__annotations__")
            },  # `int` is a built-in so is excluded from sources.
            lineno=11,
        ),
    ]

    assert_GetFrame(rpc_stub, "test_outside_func")
