from cyberbrain import Binding, Return, Symbol, InitialValue


def test_multiple_decorators(trace, check_golden_file):
    def my_decorator(f):
        def inner(*args):
            a = 1
            f(*args)
            b = a

        return inner

    @my_decorator
    @my_decorator
    @my_decorator
    @trace
    def original_function(number):
        a = [1, 2, 3]
        b = number

    original_function(1)
