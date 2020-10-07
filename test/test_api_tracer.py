from cyberbrain import Binding, Symbol


def test_api_tracer(tracer, rpc_stub):
    tracer.start()
    a = 1
    tracer.stop()

    assert tracer.events == [
        Binding(lineno=6, target=Symbol("a"), value="1", sources=set())
    ]

    from utils import assert_GetFrame

    assert_GetFrame(rpc_stub, "test_api_tracer")
