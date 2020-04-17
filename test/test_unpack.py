def test_unpack(tracer):
    l1 = [1, 2]
    numbers = [1, 2, 3, 4]
    m1 = m2 = {1: 2}

    tracer.init()

    a, b = "hi"  # UNPACK_SEQUENCE
    a, b = l1  # UNPACK_SEQUENCE
    first, *rest = numbers  # UNPACK_EX
    *beginning, last = numbers  # UNPACK_EX
    head, *middle, tail = numbers  # UNPACK_EX
    a = *l1, *numbers
    a = [*l1, *numbers]
    a = {*l1, *numbers}
    a = {**m1, **m2}

    # TODO: Test dictionary items() unpack once iter_xx, call_xx, block_xx are done.

    tracer.register()

    assert tracer.logger.changes == [
        {"target": "a", "value": "h", "sources": set()},
        {"target": "b", "value": "i", "sources": set()},
        {"target": "a", "value": 1, "sources": {"l1"}},
        {"target": "b", "value": 2, "sources": {"l1"}},
        {"target": "first", "value": 1, "sources": {"numbers"}},
        {"target": "rest", "value": [2, 3, 4], "sources": {"numbers"}},
        {"target": "beginning", "value": [1, 2, 3], "sources": {"numbers"}},
        {"target": "last", "value": 4, "sources": {"numbers"}},
        {"target": "head", "value": 1, "sources": {"numbers"}},
        {"target": "middle", "value": [2, 3], "sources": {"numbers"}},
        {"target": "tail", "value": 4, "sources": {"numbers"}},
        {"target": "a", "value": (1, 2, 1, 2, 3, 4), "sources": {"l1", "numbers"}},
        {"target": "a", "value": [1, 2, 1, 2, 3, 4], "sources": {"l1", "numbers"}},
        {"target": "a", "value": {1, 2, 1, 2, 3, 4}, "sources": {"l1", "numbers"}},
        {"target": "a", "value": {1: 2}, "sources": {"m1", "m2"}},
    ]
