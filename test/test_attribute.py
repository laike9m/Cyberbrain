from hamcrest import *

from cyberbrain import InitialValue, Mutation


# An edge case that is not handled:
# x = a.b
# x.foo = bar
#
# a is also changed, but right now we won't be able to know it.
# We need a Symbol class to handle this case, like: Symbol('x', references={'a'})
#
# H: 其实我更多想的时，Symbol 可以引用别的 symbol
# L: 引用别的 symbol 虽然或许可以让 backtracking 更简单，如果是引用所有相关 symbol 感觉有点滥用， 引
#    用一些局部（比如同一个 statement）的 symbol 应该是可以的


def test_attribute(tracer):
    class A:
        pass

    a1 = A()
    a2 = A()
    a2.y = 1

    tracer.init()

    a1.x = a2  # STORE_ATTR
    a1.x.y = 2  # LOAD_ATTR, STORE_ATTR
    del a1.x  # DELETE_ATTR

    tracer.register()

    assert_that(
        tracer.events,
        has_entries(
            {
                "a1": contains_exactly(
                    all_of(
                        instance_of(InitialValue),
                        has_properties(
                            {
                                "target": "a1",
                                "value": all_of(
                                    instance_of(A), not_(has_property("x"))
                                ),
                                "lineno": 28,
                            }
                        ),
                    ),
                    all_of(
                        instance_of(Mutation),
                        has_properties(
                            {
                                "target": "a1",
                                "value": has_property("x", has_property("y", 1)),
                                "sources": {"a2"},
                                "lineno": 28,
                            }
                        ),
                    ),
                    all_of(
                        instance_of(Mutation),
                        has_properties(
                            {
                                "target": "a1",
                                "value": has_property("x", has_property("y", 2)),
                                "sources": set(),
                                "lineno": 29,
                            }
                        ),
                    ),
                    all_of(
                        instance_of(Mutation),
                        has_properties(
                            {
                                "target": "a1",
                                "value": not_(has_property("x")),
                                "sources": set(),
                                "lineno": 30,
                            }
                        ),
                    ),
                )
            }
        ),
    )
