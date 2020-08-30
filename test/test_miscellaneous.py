from cyberbrain import InitialValue, Binding, Mutation, Deletion, Symbol
from utils import assert_GetFrame

g = 0


def test_miscellaneous(tracer, rpc_stub):
    a = "a"
    b = "b"
    c = "c"
    d = "d"
    e = [1, 2, 3]

    tracer.start()

    x = f"{a} {b:4} {c!r} {d!r:4}"  # FORMAT_VALUE, BUILD_STRING
    x = a == b == c  # ROT_THREE, _COMPARE_OP
    e[0] += e.pop()  # DUP_TOP_TWO
    del e  # DELETE_FAST
    global g
    x = g
    g = 1  # STORE_GLOBAL
    del g  # DELETE_GLOBAL

    tracer.stop()

    assert tracer.events == [
        InitialValue(target=Symbol("a"), value="a", lineno=16),
        InitialValue(target=Symbol("b"), value="b", lineno=16),
        InitialValue(target=Symbol("c"), value="c", lineno=16),
        InitialValue(target=Symbol("d"), value="d", lineno=16),
        Binding(
            target=Symbol("x"),
            value="a b    'c' 'd' ",
            sources={Symbol("a"), Symbol("b"), Symbol("d"), Symbol("c")},
            lineno=16,
        ),
        Binding(
            target=Symbol("x"),
            value=False,
            sources={Symbol("a"), Symbol("b")},
            lineno=17,
        ),
        InitialValue(target=Symbol("e"), value=[1, 2, 3], lineno=18),
        Mutation(target=Symbol("e"), value=[1, 2], lineno=18),
        Mutation(target=Symbol("e"), value=[4, 2], sources={Symbol("e")}, lineno=18),
        Deletion(target=Symbol("e"), lineno=19),
        InitialValue(target=Symbol("g"), value=0, lineno=21),
        Binding(target=Symbol("x"), value=0, sources={Symbol("g")}, lineno=21),
        Binding(target=Symbol("g"), value=1, lineno=22),
        Deletion(target=Symbol("g"), lineno=23),
    ]

    assert_GetFrame(rpc_stub, "test_miscellaneous")
