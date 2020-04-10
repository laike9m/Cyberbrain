def test_unary_operations(tracer):
    tracer.init()

    a = 1
    b = +a
    b = -a
    b = not a
    b = ~a

    tracer.register()

    assert tracer.logger.mutations == [
        {"target": "a", "value": 1, "sources": set()},
        {"target": "b", "value": 1, "sources": {"a"}},
        {"target": "b", "value": -1, "sources": {"a"}},
        {"target": "b", "value": False, "sources": {"a"}},
        {"target": "b", "value": -2, "sources": {"a"}},
    ]
