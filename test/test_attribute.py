from cyberbrain import InitialValue, Mutation, Symbol


def test_attribute(tracer, check_golden_file):
    class A:
        pass

    a1 = A()
    a2 = A()
    a2.y = 1

    tracer.start()

    a1.x = a2  # STORE_ATTR
    a1.x.y = 2  # LOAD_ATTR, STORE_ATTR
    del a1.x  # DELETE_ATTR

    tracer.stop()
