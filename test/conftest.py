import grpc
import pytest

from cyberbrain import _Tracer, _TracerFSM
from cyberbrain import trace as trace_decorator
from cyberbrain.generated import communication_pb2_grpc


def pytest_addoption(parser):
    parser.addoption("--debug_mode", action="store_true", default=False)


@pytest.fixture(scope="function")
def tracer(request):
    # We still create a new Tracer object for each test to make sure Tracer has a fresh
    # state for each test.
    return _Tracer(debug_mode=request.config.getoption("--debug_mode"))


@pytest.fixture(scope="function")
def trace(request):
    trace_decorator.debug_mode = request.config.getoption("--debug_mode")
    yield trace_decorator

    # Do cleanup because the trace decorator is reused across tests.
    trace_decorator.raw_frame = None
    trace_decorator.decorated_function_code_id = None
    trace_decorator.frame_logger = None
    trace_decorator.tracer_state = _TracerFSM.INITIAL


@pytest.fixture(scope="function")
def rpc_stub(request):
    port_picked = request.getfixturevalue("tracer").server.port
    channel = grpc.insecure_channel(f"localhost:{port_picked}")
    return communication_pb2_grpc.CommunicationStub(channel)
