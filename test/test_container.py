import os

from cyberbrain import Binding, InitialValue, Symbol, Mutation


def test_container(tracer, check_golden_file):
    a = b = 1
    c = 2
    e = 0

    tracer.start()

    d = [a, b]  # BUILD_LIST
    d = (a, b)  # BUILD_TUPLE
    d = {a, b}  # BUILD_SET
    d = {a: b}  # BUILD_MAP
    d = {1: a, 2: b}  # BUILD_CONST_KEY_MAP
    d[a] = c  # STORE_SUBSCR
    del d[a]  # DELETE_SUBSCR
    d = [a, b, c][e:c]  # BUILD_SLICE,[1,1,2][0:2]
    d = [b, b, c][e:c:a]  # BUILD_SLICE,[1,1,2][0:2:1]

    os.environ["foo"] = "bar"  # STORE_SUBSCR without emitting any event.

    tracer.stop()
