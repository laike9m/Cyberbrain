def test_container(tracer):
    a = b = 1
    c = 2

    tracer.init()

    d = [a, b]  # BUILD_LIST
    d = (a, b)  # BUILD_TUPLE
    d = {a, b}  # BUILD_SET
    d = {a: a, a: b}  # BUILD_MAP
    d = {1: a, 2: b}  # BUILD_CONST_KEY_MAP
    d[a] = c  # STORE_SUBSCR
    del d[a]  # DELETE_SUBSCR

    tracer.register()

    assert tracer.logger.mutations == [
        {"target": "d", "value": [1, 1], "sources": {"a", "b"}},
        {"target": "d", "value": (1, 1), "sources": {"a", "b"}},
        {"target": "d", "value": {1}, "sources": {"a", "b"}},
        {"target": "d", "value": {1: 1}, "sources": {"a", "b"}},
        {"target": "d", "value": {1: 1, 2: 1}, "sources": {"a", "b"}},
        {"target": "d", "value": {1: 2, 2: 1}, "sources": {"a", "c"}},
        {"target": "d", "value": {2: 1}, "sources": {"a"}},
    ]
