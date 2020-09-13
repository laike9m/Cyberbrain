from cyberbrain import trace


def test_decorator_api(rpc_stub):
    @trace
    def decorated_func():
        a = 1
        return a

    assert decorated_func() == 1

    from utils import assert_GetFrame

    assert_GetFrame(rpc_stub, "decorated_func")
