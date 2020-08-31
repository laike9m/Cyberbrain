from cyberbrain import Binding, Symbol
from utils import assert_GetFrame


def test_list_comprehension(tracer, rpc_stub):
    tracer.start()

    n = 2
    x = [i for i in range(n)]  # MAKE_FUNCTION, GET_ITER, CALL_FUNCTION
    lst = ["foo", "bar"]
    x = [e for e in lst]

    tracer.stop()

    assert tracer.events == [
        Binding(target=Symbol("n"), value=2, lineno=8),
        Binding(target=Symbol("x"), value=[0, 1], lineno=9, sources={Symbol("n")}),
        Binding(target=Symbol("lst"), value=["foo", "bar"], lineno=10),
        Binding(
            target=Symbol("x"), value=["foo", "bar"], lineno=11, sources={Symbol("lst")}
        ),
    ]

    assert_GetFrame(rpc_stub, "test_list_comprehension")
