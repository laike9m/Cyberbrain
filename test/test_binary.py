from cyberbrain import Binding, InitialValue, Symbol


def test_binary_operation(tracer, check_golden_file):
    a = b = 1
    lst = [0, 1]

    tracer.start()

    c = a**b  # BINARY_POWER
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
    c = a is b  # <3.9: COMPARE_OP,>=3.9: IS_OP
    c = a in lst  # <3.9: COMPARE_OP,>=3.9: CONTAINS_OP

    tracer.stop()
