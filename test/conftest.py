from __future__ import annotations

import os
from concurrent import futures
from threading import Thread

import grpc
import pytest
from google.protobuf import text_format
from google.protobuf.empty_pb2 import Empty

from cyberbrain import _Tracer, _TracerFSM
from cyberbrain import trace as trace_decorator
from cyberbrain.generated import communication_pb2_grpc, communication_pb2
from utils import python_version


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
        cls.server.add_insecure_port(f"[::]:1989")
        cls.server.start()
        print("Listening...")
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
