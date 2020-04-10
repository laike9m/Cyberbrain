def test_binary_operation(tracer):
    a = b = 1
    l = [0, 1]

    tracer.init()

    c = a ** b
    c = a * b
    c = a // b
    c = a / b
    c = a % b
    c = a + b
    c = a - b
    c = l[a]
    c = a << b
    c = a >> b
    c = a & b
    c = a ^ b
    c = a | b

    tracer.register()

    assert tracer.logger.mutations == [
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
