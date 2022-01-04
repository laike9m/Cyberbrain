import sys
from cyberbrain import Binding, Symbol, JumpBackToLoopStart


def test_walrus_in_while(trace, check_golden_file):
    @trace
    def walrus_in_while():
        i = 0
        while (i := i + 1) < 3:
            a = i

    walrus_in_while()

    # This test is for demonstrating https://git.io/JSX25
    if sys.version_info < (3, 10):
        assert trace.events[3:5] == [
            JumpBackToLoopStart(lineno=10, index=3, jump_target=4),
            Binding(
                lineno=9,
                index=4,
                target=Symbol("i"),
                value="2",
                sources={Symbol("i")},
            ),
        ]
    else:
        assert trace.events[3:5] == [
            Binding(
                lineno=9,
                index=3,
                target=Symbol("i"),
                value="2",
                sources={Symbol("i")},
            ),
            JumpBackToLoopStart(lineno=10, index=4, jump_target=20),
        ]
