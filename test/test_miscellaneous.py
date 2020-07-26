from cyberbrain import InitialValue, Binding, Mutation, Deletion, Symbol

g = 0


def test_miscellaneous(tracer):
    a = "a"
    b = "b"
    c = "c"
    d = "d"
    e = [1, 2, 3]

    tracer.init()

    x = f"{a} {b:4} {c!r} {d!r:4}"  # FORMAT_VALUE, BUILD_STRING
    x = a == b == c  # ROT_THREE, _COMPARE_OP
    e[0] += e.pop()  # DUP_TOP_TWO
    del e  # DELETE_FAST
    global g
    x = g
    g = 1  # STORE_GLOBAL
    del g  # DELETE_GLOBAL

    tracer.register()

    assert tracer.events == {
        "a": [InitialValue(target=Symbol("a"), value="a", lineno=15)],
        "b": [InitialValue(target=Symbol("b"), value="b", lineno=15)],
        "c": [InitialValue(target=Symbol("c"), value="c", lineno=15)],
        "d": [InitialValue(target=Symbol("d"), value="d", lineno=15)],
        "x": [
            Binding(
                target=Symbol("x"),
                value="a b    'c' 'd' ",
                sources={Symbol("a"), Symbol("b"), Symbol("d"), Symbol("c")},
                lineno=15,
            ),
            Mutation(
                target=Symbol("x"),
                value=False,
                sources={Symbol("a"), Symbol("b")},
                lineno=16,
            ),
            Mutation(target=Symbol("x"), value=0, sources={Symbol("g")}, lineno=20),
        ],
        "e": [
            InitialValue(target=Symbol("e"), value=[1, 2, 3], lineno=17),
            Mutation(target=Symbol("e"), value=[1, 2], lineno=17),
            Mutation(
                target=Symbol("e"), value=[4, 2], sources={Symbol("e")}, lineno=17
            ),
            Deletion(target=Symbol("e"), lineno=18),
        ],
        "g": [
            InitialValue(target=Symbol("g"), value=0, lineno=20),
            Mutation(target=Symbol("g"), value=1, lineno=21),
            Deletion(target=Symbol("g"), lineno=22),
        ],
    }
