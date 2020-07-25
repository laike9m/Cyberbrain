"""Test instructions that create blocks.

These tests are for Python > 3.8 only, because the syntax used are considered invalid in
Python < 3.8.
"""

import sys

import pytest

from cyberbrain import Binding, Mutation


@pytest.mark.skipif(
    sys.version_info < (3, 8),
    reason="Python version 3.7 does not support 'continue' inside 'finally' clause .",
)
def test_continue_in_finally(tracer):
    tracer.init()

    for x in range(2):
        try:
            pass
        finally:
            continue  # BREAK_LOOP (3.7) POP_FINALLY (3.8)

    tracer.register()

    assert tracer.events == {
        "x": [
            Binding(target="x", value=0, lineno=21),
            Mutation(target="x", value=1, lineno=21),
        ]
    }


@pytest.mark.skipif(
    sys.version_info < (3, 8),
    reason="Python version 3.7 does not support 'continue' inside 'finally' clause .",
)
def test_continue_in_finally_with_exception(tracer):
    """Tests POP_FINALLY when tos is an exception."""

    tracer.init()

    # If the finally clause executes a return, break or continue statement, the saved
    # exception is discarded.
    for x in range(2):
        try:
            raise IndexError
        finally:
            continue  # BREAK_LOOP (3.7) POP_FINALLY (3.8)

    tracer.register()

    assert tracer.events == {
        "x": [
            Binding(target="x", value=0, lineno=48),
            Mutation(target="x", value=1, lineno=48),
        ]
    }
