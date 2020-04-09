def test_hello(tracer):
    tracer.init()
    x = "hello world"
    y = x
    tracer.register()

    assert tracer.logger.mutations == [
        {"target": "x", "value": "hello world", "source": None},
        {"target": "y", "value": "hello world", "source": "x"},
    ]
