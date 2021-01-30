from cyberbrain import Binding, Symbol


def test_api_tracer(tracer, mocked_responses):
    tracer.start()
    a = 1
    tracer.stop()

    assert tracer.events == [
        Binding(lineno=6, target=Symbol("a"), value="1", sources=set())
    ]
