from cyberbrain import Binding, Mutation, Symbol


def test_loop(tracer, rpc_stub):
    tracer.start_tracing()

    for x in range(2):  # SETUP_LOOP (3.7), GET_ITER, FOR_ITER
        y = x  # POP_BLOCK (3.7)

    for y in range(2):
        break  # BREAK_LOOP (3.7), JUMP_ABSOLUTE (>=3.8)
        a = 1

    for z in range(1):
        continue  # CONTINUE_LOOP (3.7), JUMP_ABSOLUTE (>=3.8)
        a = 1

    i = 0
    while i < 1:  # SETUP_LOOP (3.7), POP_JUMP_IF_FALSE
        i += 1

    tracer.stop_tracing()

    assert tracer.event_sequence == [
        Binding(target=Symbol("x"), value=0, lineno=7),
        Binding(target=Symbol("y"), value=0, lineno=8, sources={Symbol("x")}),
        Binding(target=Symbol("x"), value=1, lineno=7),
        Binding(target=Symbol("y"), value=1, lineno=8, sources={Symbol("x")}),
        Binding(target=Symbol("y"), value=0, lineno=10),
        Binding(target=Symbol("z"), value=0, lineno=14),
        Binding(target=Symbol("i"), value=0, lineno=18),
        Mutation(target=Symbol("i"), value=1, sources={Symbol("i")}, lineno=20),
    ]


def test_list_comprehension(tracer, rpc_stub):
    tracer.start_tracing()

    n = 2
    x = [i for i in range(n)]  # MAKE_FUNCTION, GET_ITER, CALL_FUNCTION
    lst = ["foo", "bar"]
    x = [e for e in lst]

    tracer.stop_tracing()

    assert tracer.event_sequence == [
        Binding(target=Symbol("n"), value=2, lineno=39),
        Binding(target=Symbol("x"), value=[0, 1], lineno=40, sources={Symbol("n")}),
        Binding(target=Symbol("lst"), value=["foo", "bar"], lineno=41),
        Binding(
            target=Symbol("x"), value=["foo", "bar"], lineno=42, sources={Symbol("lst")}
        ),
    ]
