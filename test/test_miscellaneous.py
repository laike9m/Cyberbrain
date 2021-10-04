from cyberbrain import InitialValue, Binding, Mutation, Deletion, Symbol

g = 0


def test_miscellaneous(tracer, check_golden_file):
    a = "a"
    b = "b"
    c = "c"
    d = "d"
    e = [1, 2, 3]

    tracer.start()

    x = f"{a} {b:4} {c!r} {d!r:4}"  # FORMAT_VALUE,BUILD_STRING
    x = a == b == c  # ROT_THREE,_COMPARE_OP
    e[0] += e.pop()  # DUP_TOP_TWO
    del e  # DELETE_FAST
    global g
    x = g
    g = 1  # STORE_GLOBAL
    del g  # DELETE_GLOBAL

    tracer.stop()

    assert tracer.events == [
        InitialValue(target=Symbol("a"), value='"a"', lineno=-1),
        InitialValue(target=Symbol("b"), value='"b"', lineno=-1),
        InitialValue(target=Symbol("c"), value='"c"', lineno=-1),
        InitialValue(target=Symbol("d"), value='"d"', lineno=-1),
        Binding(
            target=Symbol("x"),
            value="\"a b    'c' 'd' \"",
            sources={Symbol("a"), Symbol("b"), Symbol("d"), Symbol("c")},
            lineno=15,
        ),
        Binding(
            target=Symbol("x"),
            value="false",
            sources={Symbol("a"), Symbol("b")},
            lineno=16,
        ),
        InitialValue(target=Symbol("e"), value="[1,2,3]", lineno=-1),
        Mutation(target=Symbol("e"), value="[1,2]", sources={Symbol("e")}, lineno=17),
        Mutation(target=Symbol("e"), value="[4,2]", sources={Symbol("e")}, lineno=17),
        Deletion(target=Symbol("e"), lineno=18),
        InitialValue(target=Symbol("g"), value="0", lineno=-1),
        Binding(target=Symbol("x"), value="0", sources={Symbol("g")}, lineno=20),
        Binding(target=Symbol("g"), value="1", lineno=21),
        Deletion(target=Symbol("g"), lineno=22),
    ]
