def test_unary_operations(tracer):
    a = 1

    tracer.init()

    b = +a  # UNARY_POSITIVE
    b = -a  # UNARY_NEGATIVE
    b = not a  # UNARY_NOT
    b = ~a  # UNARY_INVERT

    tracer.register()

    assert tracer.events == [
        {"target": "b", "value": 1, "sources": {"a"}},
        {"target": "b", "value": -1, "sources": {"a"}},
        {"target": "b", "value": False, "sources": {"a"}},
        {"target": "b", "value": -2, "sources": {"a"}},
    ]
