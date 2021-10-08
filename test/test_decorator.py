from cyberbrain import Binding, Return, Symbol


def test_trace_decorated_function(trace, check_golden_file):
    def my_decorator(f):
        def inner(*args):
            a = 1
            f(*args)
            b = a

        return inner

    @my_decorator
    @trace
    def original_func():
        a = [1, 2, 3]

    original_func()
