def test_inplace_operations(tracer):
    a1 = a2 = a3 = a4 = a5 = a6 = a7 = a8 = a9 = a10 = a11 = a12 = 2
    b = 2

    tracer.init()

    a1 **= b
    a2 *= b
    a3 //= b
    a4 /= b
    a5 %= b
    a6 += b
    a7 -= b
    a8 <<= b
    a9 >>= b
    a10 &= b
    a11 ^= b
    a12 |= b

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
