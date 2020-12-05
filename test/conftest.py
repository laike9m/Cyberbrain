from __future__ import annotations

import os
from concurrent import futures
from threading import Thread

import grpc
import pytest
from google.protobuf import text_format
from google.protobuf.empty_pb2 import Empty

from cyberbrain import _TracerFSM, trace
from cyberbrain.generated import communication_pb2_grpc, communication_pb2
from utils import python_version


def pytest_addoption(parser):
    parser.addoption("--debug_mode", action="store_true", default=False)


@pytest.fixture(scope="function", name="tracer")
def fixture_tracer(request):
    trace.debug_mode = request.config.getoption("--debug_mode")

    yield trace

    # Do cleanup because the trace decorator is reused across tests.
    trace.raw_frame = None
    trace.decorated_function_code_id = None
    trace.frame_logger = None
    trace.tracer_state = _TracerFSM.INITIAL


@pytest.fixture(scope="function", name="trace")
def fixture_trace(request):
    trace.debug_mode = request.config.getoption("--debug_mode")

    yield trace

    # Do cleanup because the trace decorator is reused across tests.
    trace.raw_frame = None
    trace.decorated_function_code_id = None
    trace.frame_logger = None
    trace.tracer_state = _TracerFSM.INITIAL


class TestServer:
    """A fake server to receive gRPC requests."""

    received_frames: dict[str, communication_pb2.Frame] = {}

    class TestServicer(communication_pb2_grpc.CommunicationServicer):
        def SendFrame(self, frame: communication_pb2.Frame, context: grpc.RpcContext):
            print(f"Server got frame: {frame.metadata.frame_name}")
            TestServer.received_frames[frame.metadata.frame_name] = frame
            return Empty()

    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=20),
        compression=grpc.Compression.Gzip,
    )

    communication_pb2_grpc.add_CommunicationServicer_to_server(
        servicer=TestServicer(), server=server
    )

    @classmethod
    def start(cls):
        cls.server.add_insecure_port(f"[::]:{trace.rpc_client.port}")
        cls.server.start()
        print(f"Listening on port {trace.rpc_client.port}...")
        Thread(target=cls.server.wait_for_termination).start()

    @classmethod
    def stop(cls):
        cls.server.stop(grace=None)  # Abort all active RPCs immediately.

    @classmethod
    def assert_frame_sent(cls, frame_name: str):
        golden_filepath = f"test/data/{python_version}/{frame_name}.pbtext"

        directory = os.path.dirname(golden_filepath)
        if not os.path.exists(directory):
            os.makedirs(directory)

        # Generates golden data.
        if not os.path.exists(golden_filepath):
            with open(golden_filepath, "wt") as f:
                f.write("# proto-file: communication.proto\n# proto-message: Frame\n\n")
                f.write(str(cls.received_frames[frame_name]))
            return

        # Assuming run in root directory.
        with open(golden_filepath, "rt") as f:
            response_text = f.read()

        assert cls.received_frames[frame_name] == text_format.Parse(
            response_text, communication_pb2.Frame()
        ), cls.received_frames[frame_name]


@pytest.fixture(scope="session")
def test_server(request):
    TestServer.start()
    yield TestServer
    TestServer.stop()
