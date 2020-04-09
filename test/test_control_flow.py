def test_if(tracer):
    tracer.init()

    a = []
    if a:
        x = 1
    else:
        x = 2

    tracer.register()

    assert tracer.logger.mutations == [
        {"target": "a", "value": [], "source": None},
        {"target": "x", "value": 2, "source": None},
    ]
