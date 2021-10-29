from cyberbrain import Binding, Symbol


def test_api_tracer(tracer, check_golden_file):
    tracer.start()
    a = 1
    tracer.stop()
