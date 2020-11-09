from cyberbrain import Binding, InitialValue, Symbol  # noqa


def test_call(tracer, test_server):
    a = b = c = d = 1
    counter = 0

    tracer.start()

    def f(foo, bar, *args, **kwargs):
        nonlocal counter
        counter += 1
        return counter

    x = f(a, b)  # CALL_FUNCTION
    x = f(a, bar=b)  # CALL_FUNCTION_KW
    x = f(a, b, *(c, d))  # BUILD_TUPLE_UNPACK_WITH_CALL, CALL_FUNCTION_EX(arg=0)
    x = f(a, *(b, c), **{"key": d})  # CALL_FUNCTION_EX(arg=1)

    # CALL_FUNCTION_EX, <3.9: BUILD_MAP_UNPACK_WITH_CALL, >=3.9: DICT_MERGE
    x = f(foo=a, **{"bar": b, "key": c})

    tracer.stop()

    assert tracer.events == [
        InitialValue(lineno=10, target=Symbol("counter"), value="0"),
        Binding(
            lineno=10,
            target=Symbol("f"),
            value='{"repr": "<function test_call.<locals>.f>"}',
            sources={Symbol("counter")},
        ),
        InitialValue(lineno=15, target=Symbol("a"), value="1"),
        InitialValue(lineno=15, target=Symbol("b"), value="1"),
        Binding(
            lineno=15,
            target=Symbol("x"),
            value="1",
            sources={Symbol("a"), Symbol("b"), Symbol("f")},
        ),
        Binding(
            lineno=16,
            target=Symbol("x"),
            value="2",
            sources={Symbol("a"), Symbol("b"), Symbol("f")},
        ),
        InitialValue(lineno=17, target=Symbol("c"), value="1"),
        InitialValue(lineno=17, target=Symbol("d"), value="1"),
        Binding(
            lineno=17,
            target=Symbol("x"),
            value="3",
            sources={Symbol("d"), Symbol("f"), Symbol("a"), Symbol("c"), Symbol("b")},
        ),
        Binding(
            lineno=18,
            target=Symbol("x"),
            value="4",
            sources={Symbol("d"), Symbol("f"), Symbol("a"), Symbol("c"), Symbol("b")},
        ),
        Binding(
            lineno=21,
            target=Symbol("x"),
            value="5",
            sources={Symbol("a"), Symbol("c"), Symbol("b"), Symbol("f")},
        ),
    ]

    test_server.assert_frame_sent("test_call")
