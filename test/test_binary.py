def test_binary_operation(tracer):
    a = b = 1
    l = [0, 1]

    tracer.init()

    c = a ** b  # BINARY_POWER
    c = a * b  # BINARY_MULTIPLY
    c = a // b  # BINARY_FLOOR_DIVIDE
    c = a / b  # BINARY_TRUE_DIVIDE
    c = a % b  # BINARY_MODULO
    c = a + b  # BINARY_ADD
    c = a - b  # BINARY_SUBTRACT
    c = l[a]  # BINARY_SUBSCR
    c = a << b  # BINARY_LSHIFT
    c = a >> b  # BINARY_RSHIFT
    c = a & b  # BINARY_AND
    c = a ^ b  # BINARY_XOR
    c = a | b  # BINARY_OR

    tracer.register()

    assert tracer.changes == [
        {"target": "c", "value": 1, "sources": {"a", "b"}},
        {"target": "c", "value": 1, "sources": {"a", "b"}},
        {"target": "c", "value": 1, "sources": {"a", "b"}},
        {"target": "c", "value": 1, "sources": {"a", "b"}},
        {"target": "c", "value": 0, "sources": {"a", "b"}},
        {"target": "c", "value": 2, "sources": {"a", "b"}},
        {"target": "c", "value": 0, "sources": {"a", "b"}},
        {"target": "c", "value": 1, "sources": {"a", "l"}},
        {"target": "c", "value": 2, "sources": {"a", "b"}},
        {"target": "c", "value": 0, "sources": {"a", "b"}},
        {"target": "c", "value": 1, "sources": {"a", "b"}},
        {"target": "c", "value": 0, "sources": {"a", "b"}},
        {"target": "c", "value": 1, "sources": {"a", "b"}},
    ]
