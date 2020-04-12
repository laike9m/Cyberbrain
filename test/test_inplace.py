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

    assert tracer.logger.mutations == [
        {"target": "a1", "value": 4, "sources": {"a1", "b"}},
        {"target": "a2", "value": 4, "sources": {"a2", "b"}},
        {"target": "a3", "value": 1, "sources": {"a3", "b"}},
        {"target": "a4", "value": 1.0, "sources": {"a4", "b"}},
        {"target": "a5", "value": 0, "sources": {"a5", "b"}},
        {"target": "a6", "value": 4, "sources": {"a6", "b"}},
        {"target": "a7", "value": 0, "sources": {"a7", "b"}},
        {"target": "a8", "value": 8, "sources": {"a8", "b"}},
        {"target": "a9", "value": 0, "sources": {"a9", "b"}},
        {"target": "a10", "value": 2, "sources": {"a10", "b"}},
        {"target": "a11", "value": 0, "sources": {"a11", "b"}},
        {"target": "a12", "value": 2, "sources": {"a12", "b"}},
    ]
