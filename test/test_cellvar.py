from cyberbrain import Binding, InitialValue, Symbol, Deletion


def test_deref(tracer, mocked_responses):

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
        InitialValue(lineno=-1, target=Symbol("a"), value="1"),
        Binding(lineno=12, target=Symbol("a"), value="2", sources=set()),
        Deletion(lineno=13, target=Symbol("a")),
    ]


def test_closure(tracer, mocked_responses):
    tracer.start()

    a = 1  # LOAD_CLASSDEREF

    class Foo:
        print(a)  # LOAD_CLOSURE

    class Bar(Foo):  # LOAD_CLOSURE. If we remove super(Bar, self) it becomes LOAD_CONST
        def __init__(self):
            super(Bar, self).__init__()

    tracer.stop()

    assert tracer.events == [
        Binding(lineno=28, target=Symbol("a"), value="1"),
        Binding(
            lineno=30,
            target=Symbol("Foo"),
            value='{"py/type":"test_cellvar.test_closure.<locals>.Foo"}',
            sources={Symbol("a")},
        ),
        Binding(
            lineno=33,
            target=Symbol("Bar"),
            value='{"py/type":"test_cellvar.test_closure.<locals>.Bar"}',
            repr="<class 'test_cellvar.test_closure.<locals>.Bar'>",
            sources={Symbol("Foo")},
        ),
    ]
