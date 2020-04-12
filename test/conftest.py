import pytest

from cyberbrain import Tracer


def pytest_addoption(parser):
    parser.addoption("--debug_mode", action="store_true", default=False)


@pytest.fixture
def tracer(request):
    return Tracer(request.config.getoption("--debug_mode"))
