def test_unpack(tracer):
    l1 = [1, 2]
    numbers = [1, 2, 3, 4, 5, 6]

    tracer.init()

    a, b = "hi"  # UNPACK_SEQUENCE
    a, b = l1  # UNPACK_SEQUENCE
    a, b = b, a  # ROT_TWO
    first, *rest = numbers  # UNPACK_EX
    *beginning, last = numbers  # UNPACK_EX
    head, *middle, tail = numbers  # UNPACK_EX
    l2, (x, y) = (l1, (a, b))  # UNPACK_SEQUENCE

    # TODO: Test dictionary items() unpack once iter_xx, call_xx, block_xx are done.

    tracer.register()

    assert tracer.logger.mutations == [
        {"target": "a", "value": "h", "sources": set()},
        {"target": "b", "value": "i", "sources": set()},
        {"target": "a", "value": 1, "sources": {"l1"}},
        {"target": "b", "value": 2, "sources": {"l1"}},
        {"target": "a", "value": 2, "sources": {"b"}},
        {"target": "b", "value": 1, "sources": {"a"}},
        {"target": "first", "value": 1, "sources": {"numbers"}},
        {"target": "rest", "value": [2, 3, 4, 5, 6], "sources": {"numbers"}},
        {"target": "beginning", "value": [1, 2, 3, 4, 5], "sources": {"numbers"}},
        {"target": "last", "value": 6, "sources": {"numbers"}},
        {"target": "head", "value": 1, "sources": {"numbers"}},
        {"target": "middle", "value": [2, 3, 4, 5], "sources": {"numbers"}},
        {"target": "tail", "value": 6, "sources": {"numbers"}},
        {"target": "l2", "value": [1, 2], "sources": {"l1"}},
        {"target": "x", "value": 2, "sources": {"a", "b"}},
        {"target": "y", "value": 1, "sources": {"a", "b"}},
    ]
