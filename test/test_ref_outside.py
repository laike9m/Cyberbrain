from cyberbrain import InitialValue, Binding, Symbol, Return


def f():
    return 1


def test_ref_outside(trace, check_golden_file):
    @trace
    def test_ref_outside_inner():
        a = f()

    test_ref_outside_inner()

    assert trace.events == [
        InitialValue(lineno=-1, target=Symbol("f"), value='{"repr": "<function f>"}'),
        Binding(lineno=11, target=Symbol("a"), value="1", sources={Symbol("f")}),
        Return(lineno=11, value="null", sources=set()),
    ]
