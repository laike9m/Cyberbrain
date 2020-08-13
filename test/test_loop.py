from cyberbrain import Binding, Mutation, Symbol


def test_for_loop(tracer, rpc_stub):
    tracer.start_tracing()

    for x in range(2):  # SETUP_LOOP (3.7), GET_ITER, FOR_ITER
        y = x  # POP_BLOCK (3.7)

    tracer.stop_tracing()

    assert tracer.events == {
        "x": [
            Binding(target=Symbol("x"), value=0, lineno=7),
            Mutation(target=Symbol("x"), value=1, lineno=7),
        ],
        "y": [
            Binding(target=Symbol("y"), value=0, lineno=8, sources={Symbol("x")}),
            Mutation(target=Symbol("y"), value=1, lineno=8, sources={Symbol("x")}),
        ],
    }


def test_list_comprehension(tracer, rpc_stub):
    tracer.start_tracing()

    n = 2
    x = [i for i in range(n)]
    lst = ["foo", "bar"]
    x = [e for e in lst]

    tracer.stop_tracing()

    assert tracer.events == {
        "n": [Binding(target=Symbol("n"), value=2, lineno=27)],
        "lst": [Binding(target=Symbol("lst"), value=["foo", "bar"], lineno=29)],
        "x": [
            Binding(target=Symbol("x"), value=[0, 1], lineno=28, sources={Symbol("n")}),
            Binding(
                target=Symbol("x"),
                value=["foo", "bar"],
                lineno=30,
                sources={Symbol("lst")},
            ),
        ],
    }
