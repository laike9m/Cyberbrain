from cyberbrain import InitialValue, Binding, Symbol, Return


def f():
    return 1


def test_ref_outside(trace, test_server):
    @trace
    def test_ref_outside_inner():
        a = f()

    test_ref_outside_inner()

    assert trace.events == [
        InitialValue(lineno=11, target=Symbol("f"), value='{"repr": "<function f>"}'),
        Binding(lineno=11, target=Symbol("a"), value="1", sources={Symbol("f")}),
        Return(lineno=11, value="null", sources=set()),
    ]

    test_server.assert_frame_sent("test_ref_outside_inner")
