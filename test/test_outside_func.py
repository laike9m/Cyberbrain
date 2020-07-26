"""Certain instructions can only be tested outside of a function."""

from cyberbrain import Tracer, InitialValue, Deletion, Mutation, Symbol

tracer = Tracer()

x = 1

tracer.init()
del x  # DELETE_NAME
y: int
tracer.register()


def test_delete_name():
    assert tracer.events == {
        "x": [
            InitialValue(target=Symbol("x"), value=1, lineno=10),
            Deletion(target=Symbol("x"), lineno=10),
        ],
        "__annotations__": [
            InitialValue(target=Symbol("__annotations__"), value={}, lineno=11),
            Mutation(
                target=Symbol("__annotations__"),
                value={"y": int},
                sources={Symbol("int")},
                lineno=11,
            ),
        ],
    }
