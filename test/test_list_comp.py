from cyberbrain import Binding, Symbol


def test_list_comprehension(tracer, check_golden_file):
    tracer.start()

    n = 2
    x = [i for i in range(n)]  # MAKE_FUNCTION,GET_ITER,CALL_FUNCTION
    lst = ["foo", "bar"]
    x = [e for e in lst]

    tracer.stop()
