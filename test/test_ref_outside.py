from cyberbrain import InitialValue, Binding, Symbol, Return


def f():
    return 1


def test_ref_outside(trace, check_golden_file):
    @trace
    def test_ref_outside_inner():
        a = f()

    test_ref_outside_inner()
