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
        'a': [InitialValue(target='a', value=1)],
        'b': [InitialValue(target='b', value=1)],
        'c': [InitialValue(target='c', value=2)],
        'e': [InitialValue(target='e', value=0)],
        "d": [
            Creation(target="d", value=[1, 1], sources={"a", "b"}),
            Mutation(target="d", value=(1, 1), sources={"a", "b"}),
            Mutation(target="d", value={1}, sources={"a", "b"}),
            Mutation(target="d", value={1: 1}, sources={"a", "b"}),
            Mutation(target="d", value={1: 1, 2: 1}, sources={"a", "b"}),
            Mutation(target="d", value={1: 2, 2: 1}, sources={"a", "c"}),
            Mutation(target="d", value={2: 1}, sources={"a"}),
            Mutation(target="d", value=[1, 1], sources={"a", "b", "c", "e"}),
            Mutation(target="d", value=[1, 1], sources={"a", "b", "c", "e"}),
        ]
    }
