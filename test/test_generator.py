from cyberbrain import Symbol, Binding, InitialValue, JumpBackToLoopStart, Return
from utils import get_value  # noqa


def test_generator_function(trace, check_golden_file):
    @trace
    def generator_function(count):
        while count > 0:
            x = yield count  # YIELD_VALUE, POP_TOP, triggers a return event.
            count -= 1

    gen = generator_function(2)
    for _ in gen:
        gen.send("foo")  # Remember that .send will yield the next value.

    trace.stop()
