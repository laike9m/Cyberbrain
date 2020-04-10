def test_unary_operations(tracer):
    tracer.init()

    a = 1
    b = +a
    b = -a
    b = not a
    b = ~a

    tracer.register()

    assert tracer.logger.mutations == [
        {"target": "a", "value": 1, "source": None},
        {"target": "b", "value": 1, "source": "a"},
        {"target": "b", "value": -1, "source": "a"},
        {"target": "b", "value": False, "source": "a"},
        {"target": "b", "value": -2, "source": "a"},
    ]
