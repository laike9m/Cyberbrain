from cyberbrain import Binding, InitialValue, Symbol


def test_binary_operation(tracer, rpc_stub):
    a = b = 1
    lst = [0, 1]

    tracer.start()

    c = a ** b  # BINARY_POWER
    c = a * b  # BINARY_MULTIPLY
    c = a // b  # BINARY_FLOOR_DIVIDE
    c = a / b  # BINARY_TRUE_DIVIDE
    c = a % b  # BINARY_MODULO
    c = a + b  # BINARY_ADD
    c = a - b  # BINARY_SUBTRACT
    c = lst[a]  # BINARY_SUBSCR
    c = a << b  # BINARY_LSHIFT
    c = a >> b  # BINARY_RSHIFT
    c = a & b  # BINARY_AND
    c = a ^ b  # BINARY_XOR
    c = a | b  # BINARY_OR

    tracer.stop()

    assert tracer.events == [
        InitialValue(target=Symbol("a"), value=1, lineno=10),
        InitialValue(target=Symbol("b"), value=1, lineno=10),
        Binding(
            target=Symbol("c"), value=1, sources={Symbol("a"), Symbol("b")}, lineno=10
        ),
        Binding(
            target=Symbol("c"), value=1, sources={Symbol("a"), Symbol("b")}, lineno=11
        ),
        Binding(
            target=Symbol("c"), value=1, sources={Symbol("a"), Symbol("b")}, lineno=12
        ),
        Binding(
            target=Symbol("c"), value=1, sources={Symbol("a"), Symbol("b")}, lineno=13
        ),
        Binding(
            target=Symbol("c"), value=0, sources={Symbol("a"), Symbol("b")}, lineno=14
        ),
        Binding(
            target=Symbol("c"), value=2, sources={Symbol("a"), Symbol("b")}, lineno=15
        ),
        Binding(
            target=Symbol("c"), value=0, sources={Symbol("a"), Symbol("b")}, lineno=16
        ),
        InitialValue(target=Symbol("lst"), value=[0, 1], lineno=17),
        Binding(
            target=Symbol("c"), value=1, sources={Symbol("a"), Symbol("lst")}, lineno=17
        ),
        Binding(
            target=Symbol("c"), value=2, sources={Symbol("a"), Symbol("b")}, lineno=18
        ),
        Binding(
            target=Symbol("c"), value=0, sources={Symbol("a"), Symbol("b")}, lineno=19
        ),
        Binding(
            target=Symbol("c"), value=1, sources={Symbol("a"), Symbol("b")}, lineno=20
        ),
        Binding(
            target=Symbol("c"), value=0, sources={Symbol("a"), Symbol("b")}, lineno=21
        ),
        Binding(
            target=Symbol("c"), value=1, sources={Symbol("a"), Symbol("b")}, lineno=22
        ),
    ]

    from utils import assert_GetFrame

    assert_GetFrame(rpc_stub, "test_binary_operation")
