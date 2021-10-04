from cyberbrain import Binding, Symbol, InitialValue, Return


def test_call_tracer_multiple_times(tracer, check_golden_file):
    tracer.start()
    a = 1
    tracer.stop()

    tracer.start()  # This should have no effect
    a = 2
    tracer.stop()  # This should have no effect


def test_decorator_multiple_times(trace, check_golden_file):
    @trace
    def func(b):
        a = b
        return a

    func(1)

    assert func(2) == 2
