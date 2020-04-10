def test_hello(tracer):
    tracer.init()
    x = "hello world"
    y = x
    tracer.register()

    assert tracer.logger.mutations == [
        {"target": "x", "value": "hello world", "sources": set()},
        {"target": "y", "value": "hello world", "sources": {"x"}},
    ]
