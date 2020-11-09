from cyberbrain import Binding, Symbol


def test_api_tracer(tracer, test_server):
    tracer.start()
    a = 1
    tracer.stop()

    assert tracer.events == [
        Binding(lineno=6, target=Symbol("a"), value="1", sources=set())
    ]

    test_server.assert_frame_sent("test_api_tracer")
