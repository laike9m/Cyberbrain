from cyberbrain import Binding, InitialValue, Symbol  # noqa


def test_call(tracer, check_golden_file):
    a = b = c = d = 1
    counter = 0

    tracer.start()

    def f(foo, bar, *args, **kwargs):
        nonlocal counter
        counter += 1
        return counter

    x = f(a, b)  # CALL_FUNCTION
    x = f(a, bar=b)  # CALL_FUNCTION_KW
    x = f(a, b, *(c, d))  # BUILD_TUPLE_UNPACK_WITH_CALL, CALL_FUNCTION_EX(arg=0)
    x = f(a, *(b, c), **{"key": d})  # CALL_FUNCTION_EX(arg=1)

    # CALL_FUNCTION_EX, <3.9: BUILD_MAP_UNPACK_WITH_CALL, >=3.9: DICT_MERGE
    x = f(foo=a, **{"bar": b, "key": c})

    tracer.stop()
