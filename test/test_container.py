import os

from cyberbrain import Binding, InitialValue, Symbol, Mutation


def test_container(tracer, mocked_responses):
    a = b = 1
    c = 2
    e = 0

    tracer.start()

    d = [a, b]  # BUILD_LIST
    d = (a, b)  # BUILD_TUPLE
    d = {a, b}  # BUILD_SET
    d = {a: b}  # BUILD_MAP
    d = {1: a, 2: b}  # BUILD_CONST_KEY_MAP
    d[a] = c  # STORE_SUBSCR
    del d[a]  # DELETE_SUBSCR
    d = [a, b, c][e:c]  # BUILD_SLICE,[1,1,2][0:2]
    d = [b, b, c][e:c:a]  # BUILD_SLICE,[1,1,2][0:2:1]

    os.environ["foo"] = "bar"  # STORE_SUBSCR without emitting any event.

    tracer.stop()

    assert tracer.events == [
        InitialValue(target=Symbol("a"), value="1", lineno=13),
        InitialValue(target=Symbol("b"), value="1", lineno=13),
        Binding(
            target=Symbol("d"),
            value="[1,1]",
            sources={Symbol("a"), Symbol("b")},
            lineno=13,
        ),
        Binding(
            target=Symbol("d"),
            value="[1,1]",
            sources={Symbol("a"), Symbol("b")},
            lineno=14,
        ),
        Binding(
            target=Symbol("d"),
            value="[1]",
            sources={Symbol("a"), Symbol("b")},
            lineno=15,
        ),
        Binding(
            target=Symbol("d"),
            value='{"1":1}',
            sources={Symbol("a"), Symbol("b")},
            lineno=16,
        ),
        Binding(
            target=Symbol("d"),
            value='{"1":1,"2":1}',
            sources={Symbol("a"), Symbol("b")},
            lineno=17,
        ),
        InitialValue(target=Symbol("c"), value="2", lineno=18),
        Mutation(
            target=Symbol("d"),
            value='{"1":2,"2":1}',
            sources={Symbol("d"), Symbol("a"), Symbol("c")},
            lineno=18,
        ),
        Mutation(
            target=Symbol("d"),
            value='{"2":1}',
            sources={Symbol("d"), Symbol("a")},
            lineno=19,
        ),
        InitialValue(target=Symbol("e"), value="0", lineno=20),
        Binding(
            target=Symbol("d"),
            value="[1,1]",
            sources={Symbol("a"), Symbol("b"), Symbol("c"), Symbol("e")},
            lineno=20,
        ),
        Binding(
            target=Symbol("d"),
            value="[1,1]",
            sources={Symbol("a"), Symbol("b"), Symbol("c"), Symbol("e")},
            lineno=21,
        ),
    ]
