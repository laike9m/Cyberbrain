from cyberbrain import Mutation, Binding, InitialValue


def test_binary_operation(tracer):
    a = b = 1
    lst = [0, 1]

    tracer.init()

    c = a ** b  # BINARY_POWER
    c = a * b  # BINARY_MULTIPLY
    c = a // b  # BINARY_FLOOR_DIVIDE
    c = a / b  # BINARY_TRUE_DIVIDE
    c = a % b  # BINARY_MODULO
    c = a + b  # BINARY_ADD
    c = a - b  # BINARY_SUBTRACT
    c = lst[a]  # BINARY_SUBSCR
    c = a << b  # BINARY_LSHIFT
    c = a >> b  # BINARY_RSHIFT
    c = a & b  # BINARY_AND
    c = a ^ b  # BINARY_XOR
    c = a | b  # BINARY_OR

    tracer.register()

    assert tracer.events == {
        "a": [InitialValue(target="a", value=1, lineno=10)],
        "b": [InitialValue(target="b", value=1, lineno=10)],
        "lst": [InitialValue(target="lst", value=[0, 1], lineno=17)],
        "c": [
            Binding(target="c", value=1, sources={"a", "b"}, lineno=10),
            Mutation(target="c", value=1, sources={"a", "b"}, lineno=11),
            Mutation(target="c", value=1, sources={"a", "b"}, lineno=12),
            Mutation(target="c", value=1, sources={"a", "b"}, lineno=13),
            Mutation(target="c", value=0, sources={"a", "b"}, lineno=14),
            Mutation(target="c", value=2, sources={"a", "b"}, lineno=15),
            Mutation(target="c", value=0, sources={"a", "b"}, lineno=16),
            Mutation(target="c", value=1, sources={"a", "lst"}, lineno=17),
            Mutation(target="c", value=2, sources={"a", "b"}, lineno=18),
            Mutation(target="c", value=0, sources={"a", "b"}, lineno=19),
            Mutation(target="c", value=1, sources={"a", "b"}, lineno=20),
            Mutation(target="c", value=0, sources={"a", "b"}, lineno=21),
            Mutation(target="c", value=1, sources={"a", "b"}, lineno=22),
        ],
    }
