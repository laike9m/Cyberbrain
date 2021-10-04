from cyberbrain import Binding, InitialValue, Symbol


def test_unpack(tracer, check_golden_file):
    l1 = [1, 2]
    numbers = [1, 2, 3, 4]
    m1 = m2 = {1: 2}

    tracer.start()

    a, b = "hi"  # UNPACK_SEQUENCE
    a, b = l1  # UNPACK_SEQUENCE
    first, *rest = numbers  # UNPACK_EX
    *beginning, last = numbers  # UNPACK_EX
    head, *middle, tail = numbers  # UNPACK_EX
    a = *l1, *numbers  # <3.9:BUILD_TUPLE_UNPACK,>=3.9:LIST_EXTEND,LIST_TO_TUPLE
    a = [*l1, *numbers]  # <3.9:BUILD_LIST_UNPACK,>=3.9:LIST_EXTEND
    a = {*l1, *numbers}  # <3.9:BUILD_SET_UNPACK,>=3.9:SET_UPDATE
    a = {**m1, **m2}  # <3.9:BUILD_MAP_UNPACK,>=3.9:DICT_UPDATE

    # TODO:Test dictionary items() unpack once iter_xx,call_xx,block_xx are done.

    tracer.stop()
