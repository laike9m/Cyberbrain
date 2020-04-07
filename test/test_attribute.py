from cyberbrain import Tracer
from hamcrest import (
    has_property,
    contains_exactly,
    assert_that,
    equal_to,
    has_properties,
)


class A:
    pass


a1 = A()
a2 = A()
a2.y = 1

tracer = Tracer()
tracer.init()


a1.x = a2
a1.x.y = 2

tracer.register()


def test_set_attribute():
    assert_that(
        tracer.logger.mutations,
        contains_exactly(
            has_properties(
                {"target": "a1", "value": has_property("x", has_property("y", 1))}
            ),
            has_properties(
                {"target": "a1", "value": has_property("x", has_property("y", 2))}
            ),
        ),
    )
