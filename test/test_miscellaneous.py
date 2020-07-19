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
        'a': [InitialValue(target='a', value='a')],
        'b': [InitialValue(target='b', value='b')],
        'c': [InitialValue(target='c', value='c')],
        'd': [InitialValue(target='d', value='d')],
        "x": [
            Creation(target="x", value="a b    'c' 'd' ", sources={"a", "b", "d", "c"}),
            Mutation(target="x", value=False, sources={"a", "b"}),
            Mutation(target="x", value=0, sources={"g"}),
        ],
        "e": [
            InitialValue(target="e", value=[1, 2, 3]),
            Mutation(target="e", value=[1, 2], sources=set()),
            Mutation(target="e", value=[4, 2], sources={"e"}),
            Deletion(target="e"),
        ],
        "g": [
            InitialValue(target="g", value=0),
            Mutation(target="g", value=1, sources=set()),
            Deletion(target="g"),
        ],
    }
