from cyberbrain import Binding, InitialValue, Symbol, Deletion
from utils import assert_GetFrame


def test_deref(tracer, rpc_stub):

    a = 1

    def test_deref_func():
        tracer.start()
        nonlocal a
        print(a)  # LOAD_DEREF
        a = 2  # STORE_DEREF
        del a  # DELETE_DEREF
        tracer.stop()

    test_deref_func()

    assert tracer.events == [
        InitialValue(lineno=12, target=Symbol("a"), value="1"),
        Binding(lineno=13, target=Symbol("a"), value="2", sources=set()),
        Deletion(lineno=14, target=Symbol("a")),
    ]

    assert_GetFrame(rpc_stub, "test_deref_func")


def test_closure(tracer, rpc_stub):
    tracer.start()

    a = 1  # LOAD_CLASSDEREF

    class Foo:
        print(a)  # LOAD_CLOSURE

    tracer.stop()

    assert tracer.events == [
        Binding(lineno=31, target=Symbol("a"), value="1"),
        Binding(
            lineno=33,
            target=Symbol("Foo"),
            value='{"py/type": "test_cellvar.test_closure.<locals>.Foo"}',
            sources={Symbol("a")},
        ),
    ]

    assert_GetFrame(rpc_stub, "test_closure")
