"""Test instructions that create blocks.

These tests are for Python > 3.8 only, because the syntax used are considered invalid in
Python < 3.8.
"""

import sys

import pytest

from cyberbrain import Binding, Symbol
from utils import assert_GetFrame


@pytest.mark.skipif(
    sys.version_info < (3, 8),
    reason="Python version 3.7 does not support 'continue' inside 'finally' clause .",
)
def test_continue_in_finally(tracer, rpc_stub):
    tracer.start_tracing()

    for x in range(2):
        try:
            pass
        finally:
            continue  # BREAK_LOOP (3.7) POP_FINALLY (3.8)

    tracer.stop_tracing()

    assert tracer.event_sequence == [
        Binding(target=Symbol("x"), value=0, lineno=22),
        Binding(target=Symbol("x"), value=1, lineno=22),
    ]

    assert_GetFrame(rpc_stub, "test_continue_in_finally")


@pytest.mark.skipif(
    sys.version_info < (3, 8),
    reason="Python version 3.7 does not support 'continue' inside 'finally' clause .",
)
def test_continue_in_finally_with_exception(tracer, rpc_stub):
    """Tests POP_FINALLY when tos is an exception."""

    tracer.start_tracing()

    # If the finally clause executes a return, break or continue statement, the saved
    # exception is discarded.
    for x in range(2):
        try:
            raise IndexError
        finally:
            continue  # BREAK_LOOP (3.7) POP_FINALLY (3.8)

    tracer.stop_tracing()

    assert tracer.event_sequence == [
        Binding(target=Symbol("x"), value=0, lineno=49),
        Binding(target=Symbol("x"), value=1, lineno=49),
    ]

    assert_GetFrame(rpc_stub, "test_continue_in_finally_with_exception")
