def test_decorator_api(trace, rpc_stub):
    def f(foo):
        return foo

    @trace
    def decorated_func():
        a = 1
        b = f(a)
        return a

    assert decorated_func() == 1

    from utils import assert_GetFrame

    assert_GetFrame(rpc_stub, "decorated_func")
