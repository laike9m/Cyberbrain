def test_decorator_api(trace, check_golden_file):
    def f(foo):
        return foo

    @trace
    def decorated_func():
        a = 1
        b = f(a)
        return a + b

    assert decorated_func() == 2
