from hamcrest import *

from cyberbrain import InitialValue, Mutation, Symbol


def test_attribute(tracer, rpc_stub):
    class A:
        pass

    a1 = A()
    a2 = A()
    a2.y = 1

    tracer.start()

    a1.x = a2  # STORE_ATTR
    a1.x.y = 2  # LOAD_ATTR, STORE_ATTR
    del a1.x  # DELETE_ATTR

    tracer.stop()

    assert_that(
        tracer.events,
        contains_exactly(
            all_of(
                instance_of(InitialValue),
                has_properties(
                    {
                        "target": Symbol("a2"),
                        "value": all_of(instance_of(A), has_property("y")),
                        "lineno": 16,
                    }
                ),
            ),
            all_of(
                instance_of(InitialValue),
                has_properties(
                    {
                        "target": Symbol("a1"),
                        "value": all_of(instance_of(A), not_(has_property("x"))),
                        "lineno": 16,
                    }
                ),
            ),
            all_of(
                instance_of(Mutation),
                has_properties(
                    {
                        "target": Symbol("a1"),
                        "value": has_property("x", has_property("y", 1)),
                        "sources": {Symbol("a2")},
                        "lineno": 16,
                    }
                ),
            ),
            all_of(
                instance_of(Mutation),
                has_properties(
                    {
                        "target": Symbol("a1"),
                        "value": has_property("x", has_property("y", 2)),
                        "sources": set(),
                        "lineno": 17,
                    }
                ),
            ),
            all_of(
                instance_of(Mutation),
                has_properties(
                    {
                        "target": Symbol("a1"),
                        "value": not_(has_property("x")),
                        "sources": set(),
                        "lineno": 18,
                    }
                ),
            ),
        ),
    ),

    from utils import assert_GetFrame

    assert_GetFrame(rpc_stub, "test_attribute")
