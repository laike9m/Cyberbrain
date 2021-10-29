def test_disabled_tracer(tracer):
    tracer.start(disabled=True)
    a = 1
    tracer.stop()

    assert tracer.frame_logger is None, tracer.frame_logger


def test_decorator_with_argument(trace, check_golden_file):
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
