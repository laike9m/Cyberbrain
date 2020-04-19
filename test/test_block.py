"""Test instructions that create blocks."""


def test_loop(tracer):
    tracer.init()

    for x in range(2):  # SETUP_LOOP (3.7), GET_ITER, FOR_ITER
        pass  # POP_BLOCK (3.7)

    for y in range(2):
        break  # BREAK_LOOP (3.7), JUMP_ABSOLUTE (>=3.8)
        a = 1

    for z in range(1):
        continue  # CONTINUE_LOOP (3.7), JUMP_ABSOLUTE (>=3.8)
        a = 1

    i = 0
    while i < 1:  # SETUP_LOOP (3.7), POP_JUMP_IF_FALSE
        i += 1

    tracer.register()

    assert tracer.logger.changes == [
        {"target": "x", "value": 0, "sources": set()},
        {"target": "x", "value": 1, "sources": set()},
        {"target": "y", "value": 0, "sources": set()},
        {"target": "z", "value": 0, "sources": set()},
        {"target": "i", "value": 0, "sources": set()},
        {"target": "i", "value": 1, "sources": {"i"}},
    ]


def test_exception_handling(tracer):
    tracer.init()

    try:  # SETUP_EXCEPT (3.7), SETUP_FINALLY (3.8)
        raise IndexError("error")  # RAISE_VARARGS
        a = 1
    except IndexError:
        pass  # POP_EXCEPT

    tracer.register()

    assert tracer.logger.changes == []
