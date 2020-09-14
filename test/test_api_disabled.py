def test_disabled_tracer(tracer):
    tracer.start(disabled=True)
    a = 1
    tracer.stop()

    assert tracer.frame_logger is None, tracer.frame_logger


def test_decorator_with_argument(trace, rpc_stub):
    @trace(disabled=True)
    def decorated_func_disabled():
        a = 1
        return a

    @trace(disabled=False)
    def decorated_func_enabled():
        a = 2
        return a

    decorated_func_disabled()
    assert not trace.frame_logger

    decorated_func_enabled()
    assert trace.frame_logger

    from utils import assert_GetFrame

    assert_GetFrame(rpc_stub, "decorated_func_enabled")
