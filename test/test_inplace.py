from cyberbrain import InitialValue, Mutation


def test_inplace_operations(tracer):
    a1 = a2 = a3 = a4 = a5 = a6 = a7 = a8 = a9 = a10 = a11 = a12 = 2
    b = 2

    tracer.init()

    a1 **= b  # INPLACE_POWER
    a2 *= b  # INPLACE_MULTIPLY
    a3 //= b  # INPLACE_FLOOR_DIVIDE
    a4 /= b  # INPLACE_TRUE_DIVIDE
    a5 %= b  # INPLACE_MODULO
    a6 += b  # INPLACE_ADD
    a7 -= b  # INPLACE_SUBTRACT
    a8 <<= b  # INPLACE_LSHIFT
    a9 >>= b  # INPLACE_RSHIFT
    a10 &= b  # INPLACE_AND
    a11 ^= b  # INPLACE_XOR
    a12 |= b  # INPLACE_OR

    tracer.register()

    assert tracer.events == {
        "b": [InitialValue(target="b", value=2, lineno=10)],
        "a1": [
            InitialValue(target="a1", value=2, lineno=10),
            Mutation(target="a1", value=4, sources={"a1", "b"}, lineno=10),
        ],
        "a2": [
            InitialValue(target="a2", value=2, lineno=11),
            Mutation(target="a2", value=4, sources={"a2", "b"}, lineno=11),
        ],
        "a3": [
            InitialValue(target="a3", value=2, lineno=12),
            Mutation(target="a3", value=1, sources={"a3", "b"}, lineno=12),
        ],
        "a4": [
            InitialValue(target="a4", value=2, lineno=13),
            Mutation(target="a4", value=1.0, sources={"a4", "b"}, lineno=13),
        ],
        "a5": [
            InitialValue(target="a5", value=2, lineno=14),
            Mutation(target="a5", value=0, sources={"a5", "b"}, lineno=14),
        ],
        "a6": [
            InitialValue(target="a6", value=2, lineno=15),
            Mutation(target="a6", value=4, sources={"a6", "b"}, lineno=15),
        ],
        "a7": [
            InitialValue(target="a7", value=2, lineno=16),
            Mutation(target="a7", value=0, sources={"a7", "b"}, lineno=16),
        ],
        "a8": [
            InitialValue(target="a8", value=2, lineno=17),
            Mutation(target="a8", value=8, sources={"a8", "b"}, lineno=17),
        ],
        "a9": [
            InitialValue(target="a9", value=2, lineno=18),
            Mutation(target="a9", value=0, sources={"a9", "b"}, lineno=18),
        ],
        "a10": [
            InitialValue(target="a10", value=2, lineno=19),
            Mutation(target="a10", value=2, sources={"a10", "b"}, lineno=19),
        ],
        "a11": [
            InitialValue(target="a11", value=2, lineno=20),
            Mutation(target="a11", value=0, sources={"a11", "b"}, lineno=20),
        ],
        "a12": [
            InitialValue(target="a12", value=2, lineno=21),
            Mutation(target="a12", value=2, sources={"a12", "b"}, lineno=21),
        ],
    }
