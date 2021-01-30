from __future__ import annotations

import json
import msgpack
import os
import pytest
import responses

from cyberbrain import _TracerFSM, trace
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


@pytest.fixture
def mocked_responses(request):
    with responses.RequestsMock() as resp:
        resp.add(
            responses.POST,
            f"http://localhost:{trace.rpc_client.port}/frame",
            status=200,
            content_type="application/octet-stream",
        )
        yield resp

        frame_data = msgpack.unpackb(resp.calls[0].request.body)
        frame_name = frame_data["metadata"]["frame_name"]

        # Generates golden data.
        golden_filepath = f"test/data/{python_version}/{frame_name}.json"
        directory = os.path.dirname(golden_filepath)
        if not os.path.exists(directory):
            os.makedirs(directory)

        if not os.path.exists(golden_filepath):
            with open(golden_filepath, "wt") as f:
                json.dump(frame_data, f, ensure_ascii=False, indent=4)
            return

        # Assuming run in root directory.
        with open(golden_filepath, "rt") as f:
            golden_frame_data = json.loads(f.read())

        assert frame_data == golden_frame_data, json.dumps(frame_data, indent=4)
