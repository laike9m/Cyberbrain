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


def test_external_iterator(trace, mocked_responses):
    @trace
    def external_iterator_function():
        iterator = iter((1,2,3))
        x = next(iterator)
        x = next(iterator)
        return x
    
    external_iterator_function()
