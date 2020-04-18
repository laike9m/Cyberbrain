"""Test instructions that create blocks."""


def test_for_loop(tracer):
    tracer.init()

    for x in range(2):
        pass

    for y in range(2):
        break  # BREAK_LOOP (3.7), JUMP_ABSOLUTE (>=3.8)
        a = 1

    for z in range(1):
        continue  # CONTINUE_LOOP (3.7), JUMP_ABSOLUTE (>=3.8)
        a = 1

    tracer.register()

    print(tracer.logger.changes)

    assert tracer.logger.changes == [
        {"target": "x", "value": 0, "sources": set()},
        {"target": "x", "value": 1, "sources": set()},
        {"target": "y", "value": 0, "sources": set()},
        {"target": "z", "value": 0, "sources": set()},
    ]
