"""Test instructions that create blocks."""


def test_for_loop(tracer):
    tracer.init()

    for x in range(2):
        pass

    tracer.register()

    print(tracer.logger.changes)

    assert tracer.logger.changes == [
        {"target": "x", "value": 0, "sources": set()},
        {"target": "x", "value": 1, "sources": set()},
    ]
