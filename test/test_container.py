def test_container(tracer):
    a = b = c = None

    tracer.init()

    d = [a, b, c]

    tracer.register()

    print(tracer.logger.mutations)
    assert tracer.logger.mutations == [
        {"target": "d", "value": [None, None, None], "sources": {"a", "b", "c"}}
    ]
