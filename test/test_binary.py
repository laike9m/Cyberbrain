from cyberbrain import Mutation, Creation, InitialValue


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
        "a": [InitialValue(target='a', value=1)],
        'b': [InitialValue(target='b', value=1)],
        'lst': [InitialValue(target='lst', value=[0, 1])],
        "c": [
            Creation(target="c", value=1, sources={"a", "b"}),
            Mutation(target="c", value=1, sources={"a", "b"}),
            Mutation(target="c", value=1, sources={"a", "b"}),
            Mutation(target="c", value=1, sources={"a", "b"}),
            Mutation(target="c", value=0, sources={"a", "b"}),
            Mutation(target="c", value=2, sources={"a", "b"}),
            Mutation(target="c", value=0, sources={"a", "b"}),
            Mutation(target="c", value=1, sources={"a", "lst"}),
            Mutation(target="c", value=2, sources={"a", "b"}),
            Mutation(target="c", value=0, sources={"a", "b"}),
            Mutation(target="c", value=1, sources={"a", "b"}),
            Mutation(target="c", value=0, sources={"a", "b"}),
            Mutation(target="c", value=1, sources={"a", "b"}),
        ]
    }
