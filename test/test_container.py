from cyberbrain import Mutation, Binding, InitialValue, Symbol


def test_container(tracer):
    a = b = 1
    c = 2
    e = 0

    tracer.init()

    d = [a, b]  # BUILD_LIST
    d = (a, b)  # BUILD_TUPLE
    d = {a, b}  # BUILD_SET
    d = {a: b}  # BUILD_MAP
    d = {1: a, 2: b}  # BUILD_CONST_KEY_MAP
    d[a] = c  # STORE_SUBSCR
    del d[a]  # DELETE_SUBSCR
    d = [a, b, c][e:c]  # BUILD_SLICE, [1, 1, 2][0:2]
    d = [b, b, c][e:c:a]  # BUILD_SLICE, [1, 1, 2][0:2:1]

    tracer.register()

    assert tracer.events == {
        "a": [InitialValue(target=Symbol("a"), value=1, lineno=11)],
        "b": [InitialValue(target=Symbol("b"), value=1, lineno=11)],
        "c": [InitialValue(target=Symbol("c"), value=2, lineno=16)],
        "e": [InitialValue(target=Symbol("e"), value=0, lineno=18)],
        "d": [
            Binding(
                target=Symbol("d"),
                value=[1, 1],
                sources={Symbol("a"), Symbol("b")},
                lineno=11,
            ),
            Mutation(
                target=Symbol("d"),
                value=(1, 1),
                sources={Symbol("a"), Symbol("b")},
                lineno=12,
            ),
            Mutation(
                target=Symbol("d"),
                value={1},
                sources={Symbol("a"), Symbol("b")},
                lineno=13,
            ),
            Mutation(
                target=Symbol("d"),
                value={1: 1},
                sources={Symbol("a"), Symbol("b")},
                lineno=14,
            ),
            Mutation(
                target=Symbol("d"),
                value={1: 1, 2: 1},
                sources={Symbol("a"), Symbol("b")},
                lineno=15,
            ),
            Mutation(
                target=Symbol("d"),
                value={1: 2, 2: 1},
                sources={Symbol("a"), Symbol("c")},
                lineno=16,
            ),
            Mutation(
                target=Symbol("d"), value={2: 1}, sources={Symbol("a")}, lineno=17
            ),
            Mutation(
                target=Symbol("d"),
                value=[1, 1],
                sources={Symbol("a"), Symbol("b"), Symbol("c"), Symbol("e")},
                lineno=18,
            ),
            Mutation(
                target=Symbol("d"),
                value=[1, 1],
                sources={Symbol("a"), Symbol("b"), Symbol("c"), Symbol("e")},
                lineno=19,
            ),
        ],
    }
