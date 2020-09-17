from cyberbrain import Binding, Symbol


def test_call_tracer_multiple_times(tracer):
    tracer.start()
    a = 1
    tracer.stop()

    tracer.start()  # This should have no effect
    a = 2
    tracer.stop()  # This should have no effect

    assert tracer.events == [
        Binding(lineno=6, target=Symbol("a"), value=1, sources=set())
    ]


def test_decorator_multiple_times(trace, rpc_stub):
    @trace
    def func():
        a = 1

    func()

    func()

    assert trace.events == [
        Binding(lineno=21, target=Symbol("a"), value=1, sources=set())
    ]
