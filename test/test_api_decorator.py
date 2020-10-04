def test_decorator_api(trace, rpc_stub):
    def f(foo):
        return foo

    @trace
    def decorated_func():
        a = 1
        b = f(a)
        return a + b

    assert decorated_func() == 2

    from utils import assert_GetFrame

    assert_GetFrame(rpc_stub, "decorated_func")
