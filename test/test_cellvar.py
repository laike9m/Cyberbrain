from cyberbrain import Binding, InitialValue, Symbol, Deletion


def test_deref(tracer, test_server):

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
        InitialValue(lineno=11, target=Symbol("a"), value="1"),
        Binding(lineno=12, target=Symbol("a"), value="2", sources=set()),
        Deletion(lineno=13, target=Symbol("a")),
    ]

    test_server.assert_frame_sent("test_deref_func")


def test_closure(tracer, test_server):
    tracer.start()

    a = 1  # LOAD_CLASSDEREF

    class Foo:
        print(a)  # LOAD_CLOSURE

    tracer.stop()

    assert tracer.events == [
        Binding(lineno=30, target=Symbol("a"), value="1"),
        Binding(
            lineno=32,
            target=Symbol("Foo"),
            value='{"py/type":"test_cellvar.test_closure.<locals>.Foo"}',
            sources={Symbol("a")},
        ),
    ]

    test_server.assert_frame_sent("test_closure")
