def test_miscellaneous(tracer):
    a = "a"
    b = "b"
    c = "c"
    d = "d"

    tracer.init()

    x = f"{a} {b:4} {c!r} {d!r:4}"  # FORMAT_VALUE, BUILD_STRING
    x = a == b == c  # ROT_THREE, COMPARE_OP

    tracer.register()

    print(tracer.logger.mutations)

    assert tracer.logger.mutations == [
        {"target": "x", "value": "a b    'c' 'd' ", "sources": {"a", "b", "d", "c"}},
        {"target": "x", "value": False, "sources": {"a", "b"}},
    ]
