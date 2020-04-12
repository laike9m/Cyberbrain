def test_string(tracer):
    a = "a"
    b = "b"
    c = "c"
    d = "d"

    tracer.init()

    x = f"{a} {b:4} {c!r} {d!r:4}"

    tracer.register()

    print(tracer.logger.mutations)

    assert tracer.logger.mutations == [
        {"target": "x", "value": "a b    'c' 'd' ", "sources": {"a", "b", "d", "c"}},
    ]
