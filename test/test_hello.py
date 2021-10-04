from cyberbrain import Binding, Symbol


def test_hello(tracer, check_golden_file):
    tracer.start()
    x = "hello world"  # LOAD_CONST, STORE_FAST
    y = x  # LOAD_FAST, STORE_FAST
    x, y = y, x  # ROT_TWO, STORE_FAST
    tracer.stop()
