import grpc
import pytest

from cyberbrain import _Tracer
from cyberbrain.generated import communication_pb2_grpc


def pytest_addoption(parser):
    parser.addoption("--debug_mode", action="store_true", default=False)


@pytest.fixture(scope="function")
def tracer(request):
    # We still create a new Tracer object for each test to make sure Tracer has a fresh
    # state for each test.
    return _Tracer(debug_mode=request.config.getoption("--debug_mode"))


@pytest.fixture(scope="function")
def rpc_stub(request):
    port_picked = request.getfixturevalue("tracer").server.port
    channel = grpc.insecure_channel(f"localhost:{port_picked}")
    return communication_pb2_grpc.CommunicationStub(channel)
