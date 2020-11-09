"""Test instructions that create blocks.

These tests are for Python > 3.8 only, because the syntax used are considered invalid in
Python < 3.8.
"""

import sys

import pytest

from cyberbrain import Binding, Symbol, JumpBackToLoopStart, Loop
from utils import get_value


@pytest.mark.skipif(
    sys.version_info < (3, 8),
    reason="Python version 3.7 does not support 'continue' inside 'finally' clause .",
)
def test_continue_in_finally(tracer, test_server):
    tracer.start()

    for x in range(2):
        try:
            pass
        finally:
            continue  # 3.8: POP_FINALLY, >= 3.9: POP_EXCEPT, RERAISE

    tracer.stop()

    assert tracer.events == [
        Binding(target=Symbol("x"), value="0", lineno=22),
        JumpBackToLoopStart(lineno=26, jump_target=16),
        Binding(target=Symbol("x"), value="1", lineno=22),
        JumpBackToLoopStart(lineno=26, jump_target=16),
    ]
    assert tracer.loops == [
        Loop(
            start_offset=16,
            end_offset=get_value({"py38": 32, "default": 24}),
            start_lineno=22,
        )
    ]

    test_server.assert_frame_sent("test_continue_in_finally")


@pytest.mark.skipif(
    sys.version_info < (3, 8),
    reason="Python version 3.7 does not support 'continue' inside 'finally' clause .",
)
def test_continue_in_finally_with_exception(tracer, test_server):
    """Tests POP_FINALLY when tos is an exception."""

    tracer.start()

    # If the finally clause executes a return, break or continue statement, the saved
    # exception is discarded.
    for x in range(2):
        try:
            raise IndexError
        finally:
            continue  # BREAK_LOOP (3.7) POP_FINALLY (3.8)

    tracer.stop()

    assert tracer.events == [
        Binding(target=Symbol("x"), value="0", lineno=58),
        JumpBackToLoopStart(lineno=62, jump_target=16),
        Binding(target=Symbol("x"), value="1", lineno=58),
        JumpBackToLoopStart(lineno=62, jump_target=16),
    ]
    assert tracer.loops == [
        Loop(
            start_offset=16,
            end_offset=get_value({"py38": 36, "default": 40}),
            start_lineno=58,
        )
    ]

    test_server.assert_frame_sent("test_continue_in_finally_with_exception")
