from cyberbrain import InitialValue, Creation, Mutation, Deletion

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
        "a": [InitialValue(target="a", value="a", lineno=15)],
        "b": [InitialValue(target="b", value="b", lineno=15)],
        "c": [InitialValue(target="c", value="c", lineno=15)],
        "d": [InitialValue(target="d", value="d", lineno=15)],
        "x": [
            Creation(
                target="x",
                value="a b    'c' 'd' ",
                sources={"a", "b", "d", "c"},
                lineno=15,
            ),
            Mutation(target="x", value=False, sources={"a", "b"}, lineno=16),
            Mutation(target="x", value=0, sources={"g"}, lineno=20),
        ],
        "e": [
            InitialValue(target="e", value=[1, 2, 3], lineno=17),
            Mutation(target="e", value=[1, 2], lineno=17),
            Mutation(target="e", value=[4, 2], sources={"e"}, lineno=17),
            Deletion(target="e", lineno=18),
        ],
        "g": [
            InitialValue(target="g", value=0, lineno=20),
            Mutation(target="g", value=1, lineno=21),
            Deletion(target="g", lineno=22),
        ],
    }
