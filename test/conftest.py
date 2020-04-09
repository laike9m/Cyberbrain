import pytest

from cyberbrain import Tracer


@pytest.fixture
def tracer():
    return Tracer()
