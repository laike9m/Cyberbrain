"""Certain instructions can only be tested outside of a function."""

from cyberbrain import Tracer, InitialValue, Deletion, Mutation

tracer = Tracer()

x = 1

tracer.init()
del x  # DELETE_NAME
y: int
tracer.register()


def test_delete_name():
    assert tracer.events == {
        "x": [
            InitialValue(target="x", value=1, lineno=10),
            Deletion(target="x", lineno=10),
        ],
        "__annotations__": [
            InitialValue(target="__annotations__", value={}, lineno=11),
            Mutation(
                target="__annotations__", value={"y": int}, sources={"int"}, lineno=11
            ),
        ],
    }
