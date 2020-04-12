def test_if(tracer):
    a = []

    tracer.init()

    if a:  # POP_JUMP_IF_FALSE
        x = 1  # JUMP_FORWARD
    else:
        x = 2

    tracer.register()

    assert tracer.logger.mutations == [
        {"target": "x", "value": 2, "sources": set()},
    ]
