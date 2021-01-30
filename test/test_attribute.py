from cyberbrain import InitialValue, Mutation, Symbol


def test_attribute(tracer, mocked_responses):
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

    assert tracer.events == [
        InitialValue(
            lineno=14,
            target=Symbol("a2"),
            value='{"y":1}',
            repr="<test_attribute.test_attribute.<locals>.A object>",
        ),
        InitialValue(
            lineno=14,
            target=Symbol("a1"),
            value="{}",
            repr="<test_attribute.test_attribute.<locals>.A object>",
        ),
        Mutation(
            lineno=14,
            target=Symbol("a1"),
            sources={Symbol("a2"), Symbol("a1")},
            value='{"x":{"y":1}}',
            repr="<test_attribute.test_attribute.<locals>.A object>",
        ),
        Mutation(
            lineno=15,
            target=Symbol("a1"),
            sources={Symbol("a1")},
            value='{"x":{"y":2}}',
            repr="<test_attribute.test_attribute.<locals>.A object>",
        ),
        Mutation(
            lineno=16,
            target=Symbol("a1"),
            sources={Symbol("a1")},
            value="{}",
            repr="<test_attribute.test_attribute.<locals>.A object>",
        ),
    ]
