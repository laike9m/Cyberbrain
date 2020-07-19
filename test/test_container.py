from cyberbrain import Mutation, Creation, InitialValue


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
        "a": [InitialValue(target="a", value=1, lineno=11)],
        "b": [InitialValue(target="b", value=1, lineno=11)],
        "c": [InitialValue(target="c", value=2, lineno=16)],
        "e": [InitialValue(target="e", value=0, lineno=18)],
        "d": [
            Creation(target="d", value=[1, 1], sources={"a", "b"}, lineno=11),
            Mutation(target="d", value=(1, 1), sources={"a", "b"}, lineno=12),
            Mutation(target="d", value={1}, sources={"a", "b"}, lineno=13),
            Mutation(target="d", value={1: 1}, sources={"a", "b"}, lineno=14),
            Mutation(target="d", value={1: 1, 2: 1}, sources={"a", "b"}, lineno=15),
            Mutation(target="d", value={1: 2, 2: 1}, sources={"a", "c"}, lineno=16),
            Mutation(target="d", value={2: 1}, sources={"a"}, lineno=17),
            Mutation(target="d", value=[1, 1], sources={"a", "b", "c", "e"}, lineno=18),
            Mutation(target="d", value=[1, 1], sources={"a", "b", "c", "e"}, lineno=19),
        ],
    }
