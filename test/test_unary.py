from cyberbrain import Binding, InitialValue, Symbol


def test_unary_operations(tracer, check_golden_file):
    a = 1

    tracer.start()

    b = +a  # UNARY_POSITIVE
    b = -a  # UNARY_NEGATIVE
    b = not a  # UNARY_NOT
    b = ~a  # UNARY_INVERT

    tracer.stop()
