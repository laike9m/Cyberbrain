from cyberbrain import tracer, Binding, Symbol


def test_tracer_api(rpc_stub):
    tracer.start()
    a = 1
    tracer.stop()

    assert tracer.events == [
        Binding(lineno=6, target=Symbol("a"), value=1, sources=set())
    ]

    from utils import assert_GetFrame

    assert_GetFrame(rpc_stub, "test_tracer_api")
