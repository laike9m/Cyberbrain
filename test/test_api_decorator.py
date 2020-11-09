def test_decorator_api(trace, test_server):
    def f(foo):
        return foo

    @trace
    def decorated_func():
        a = 1
        b = f(a)
        return a + b

    assert decorated_func() == 2

    test_server.assert_frame_sent("decorated_func")
