from cyberbrain import InitialValue, Binding, Symbol


def f():
    return 1


def test_ref_outside(trace, rpc_stub):
    @trace
    def test_ref_outside_inner():
        a = f()

    test_ref_outside_inner()

    assert trace.events == [
        InitialValue(lineno=11, target=Symbol("f"), value=f),
        Binding(lineno=11, target=Symbol("a"), value=1, sources={Symbol("f")}),
    ]

    from utils import assert_GetFrame

    assert_GetFrame(rpc_stub, "test_ref_outside_inner")
