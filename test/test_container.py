def test_container(tracer):
    a = b = c = None

    tracer.init()

    d = [a, b, c]
    d = (a, b, c)
    d = {a, b, c}
    d = {a: a, a: b, a: c}  # BUILD_MAP
    d = {1: a, 2: b, 3: c}  # BUILD_CONST_KEY_MAP

    tracer.register()

    assert tracer.logger.mutations == [
        {"target": "d", "value": [None, None, None], "sources": {"a", "b", "c"}},
        {"target": "d", "value": (None, None, None), "sources": {"a", "b", "c"}},
        {"target": "d", "value": {None}, "sources": {"a", "b", "c"}},
        {"target": "d", "value": {None: None}, "sources": {"a", "b", "c"},},
        {
            "target": "d",
            "value": {1: None, 2: None, 3: None},
            "sources": {"a", "b", "c"},
        },
    ]
