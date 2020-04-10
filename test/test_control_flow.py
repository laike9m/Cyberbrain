def test_if(tracer):
    tracer.init()

    a = []
    if a:
        x = 1
    else:
        x = 2

    tracer.register()

    assert tracer.logger.mutations == [
        {"target": "a", "value": [], "sources": set()},
        {"target": "x", "value": 2, "sources": set()},
    ]
