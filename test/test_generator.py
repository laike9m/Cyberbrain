from cyberbrain import Symbol, Binding, InitialValue, JumpBackToLoopStart, Return
from utils import get_value  # noqa


def test_regular_generator_function(trace, check_golden_file):
    @trace
    def regular_generator_function(count):
        while count > 0:
            yield count  # GEN_START, YIELD_VALUE, POP_TOP, triggers a return event.
            count -= 1

    gen = regular_generator_function(2)
    for item in gen:
        x = item
        print(x)

    trace.stop()


def test_generator_function_send(trace, check_golden_file):
    @trace
    def generator_function_send(count):
        while count > 0:
            x = yield count  # GEN_START, YIELD_VALUE, POP_TOP, triggers a return event.
            count -= 1

    gen = generator_function_send(2)
    for _ in gen:
        gen.send("foo")  # Remember that .send will yield the next value.

    trace.stop()
