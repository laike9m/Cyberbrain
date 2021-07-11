def test_external_generator(trace, mocked_responses):
    def inner():
        for i in range(2):
            yield i

    @trace
    def external_generator_function():
        generator = inner()
        x = next(generator)
        x = next(generator)
        return x
    
    external_generator_function()

    # assert trace.events == [
    #     InitialValue(
    #         lineno=-1,
    #         target=Symbol("inner"),
    #         value='{"repr": "<function test_external_generator.<locals>.inner>"}',
    #         repr="<function test_external_generator.<locals>.inner>",
    #     ),
    #     Binding(
    #         lineno=106,
    #         target=Symbol("generator"),
    #         value='{"repr": "<generator object test_external_generator.<locals>.inner>"}',
    #         repr="<generator object test_external_generator.<locals>.inner>",
    #         sources=set(),
    #     ),
    #     Binding(
    #         lineno=107,
    #         target=Symbol("x"),
    #         value="0",
    #         repr="0",
    #         sources={Symbol("generator")},
    #     ),
    #     Binding(
    #         lineno=108,
    #         target=Symbol("x"),
    #         value="1",
    #         repr="1",
    #         sources={Symbol("generator")},
    #     ),
    #     Return(
    #         lineno=109,
    #         value="1",
    #         repr="1",
    #         sources={Symbol("x")},
    #     ),
    # ]

def test_external_iterator(trace, mocked_responses):
    @trace
    def external_iterator_function():
        iterator = iter((1,2,3))
        x = next(iterator)
        x = next(iterator)
        return x
    
    external_iterator_function()
