from hamcrest import *


def test_set_attribute(tracer):
    class A:
        pass

    a1 = A()
    a2 = A()
    a2.y = 1

    tracer.init()

    a1.x = a2
    a1.x.y = 2

    tracer.register()

    assert_that(
        tracer.logger.mutations,
        contains_exactly(
            has_properties(
                {
                    "target": "a1",
                    "value": has_property("x", has_property("y", 1)),
                    "sources": {"a2"},
                }
            ),
            has_properties(
                {
                    "target": "a1",
                    "value": has_property("x", has_property("y", 2)),
                    "sources": set(),
                }
            ),
        ),
    )
