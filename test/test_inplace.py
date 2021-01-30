from cyberbrain import InitialValue, Symbol, Binding


def test_inplace_operations(tracer, mocked_responses):
    a1 = a2 = a3 = a4 = a5 = a6 = a7 = a8 = a9 = a10 = a11 = a12 = 2
    b = 2

    tracer.start()

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

    tracer.stop()

    assert tracer.events == [
        InitialValue(target=Symbol("a1"), value="2", lineno=10),
        InitialValue(target=Symbol("b"), value="2", lineno=10),
        Binding(
            target=Symbol("a1"),
            value="4",
            sources={Symbol("a1"), Symbol("b")},
            lineno=10,
        ),
        InitialValue(target=Symbol("a2"), value="2", lineno=11),
        Binding(
            target=Symbol("a2"),
            value="4",
            sources={Symbol("a2"), Symbol("b")},
            lineno=11,
        ),
        InitialValue(target=Symbol("a3"), value="2", lineno=12),
        Binding(
            target=Symbol("a3"),
            value="1",
            sources={Symbol("a3"), Symbol("b")},
            lineno=12,
        ),
        InitialValue(target=Symbol("a4"), value="2", lineno=13),
        Binding(
            target=Symbol("a4"),
            value="1.0",
            sources={Symbol("a4"), Symbol("b")},
            lineno=13,
        ),
        InitialValue(target=Symbol("a5"), value="2", lineno=14),
        Binding(
            target=Symbol("a5"),
            value="0",
            sources={Symbol("a5"), Symbol("b")},
            lineno=14,
        ),
        InitialValue(target=Symbol("a6"), value="2", lineno=15),
        Binding(
            target=Symbol("a6"),
            value="4",
            sources={Symbol("a6"), Symbol("b")},
            lineno=15,
        ),
        InitialValue(target=Symbol("a7"), value="2", lineno=16),
        Binding(
            target=Symbol("a7"),
            value="0",
            sources={Symbol("a7"), Symbol("b")},
            lineno=16,
        ),
        InitialValue(target=Symbol("a8"), value="2", lineno=17),
        Binding(
            target=Symbol("a8"),
            value="8",
            sources={Symbol("a8"), Symbol("b")},
            lineno=17,
        ),
        InitialValue(target=Symbol("a9"), value="2", lineno=18),
        Binding(
            target=Symbol("a9"),
            value="0",
            sources={Symbol("a9"), Symbol("b")},
            lineno=18,
        ),
        InitialValue(target=Symbol("a10"), value="2", lineno=19),
        Binding(
            target=Symbol("a10"),
            value="2",
            sources={Symbol("a10"), Symbol("b")},
            lineno=19,
        ),
        InitialValue(target=Symbol("a11"), value="2", lineno=20),
        Binding(
            target=Symbol("a11"),
            value="0",
            sources={Symbol("a11"), Symbol("b")},
            lineno=20,
        ),
        InitialValue(target=Symbol("a12"), value="2", lineno=21),
        Binding(
            target=Symbol("a12"),
            value="2",
            sources={Symbol("a12"), Symbol("b")},
            lineno=21,
        ),
    ]
