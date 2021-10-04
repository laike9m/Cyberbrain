from cyberbrain import InitialValue, Binding, Mutation, Deletion, Symbol

g = 0


def test_miscellaneous(tracer, check_golden_file):
    a = "a"
    b = "b"
    c = "c"
    d = "d"
    e = [1, 2, 3]

    tracer.start()

    x = f"{a} {b:4} {c!r} {d!r:4}"  # FORMAT_VALUE,BUILD_STRING
    x = a == b == c  # ROT_THREE,_COMPARE_OP
    e[0] += e.pop()  # DUP_TOP_TWO
    del e  # DELETE_FAST
    global g
    x = g
    g = 1  # STORE_GLOBAL
    del g  # DELETE_GLOBAL

    tracer.stop()
