from __future__ import annotations

import json
import msgpack
import os
import pytest
import responses
import attr

from cyberbrain import _TracerFSM, trace, Symbol
from utils import python_version, get_os_type


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


def get_golden_data(golden_filepath, key):
    directory = os.path.dirname(golden_filepath)
    if not os.path.exists(directory):
        os.makedirs(directory)

    if not os.path.exists(golden_filepath):
        return None

    with open(golden_filepath, "r") as f:
        golden_frame_data = json.load(f)
    return golden_frame_data.get(key)


def update_golden_data(golden_filepath, key, value):
    golden_frame_data = {}
    if os.path.exists(golden_filepath):
        with open(golden_filepath, "r") as f:
            golden_frame_data = json.load(f)

    golden_frame_data[key] = value

    with open(golden_filepath, "w") as f:
        json.dump(golden_frame_data, f, ensure_ascii=False, indent=4)


def serialize_symbol(symbol):
    snapshot = symbol.snapshot and {
        "location": symbol.snapshot.location,
        "events_pointer": symbol.snapshot.events_pointer,
    }
    return {"name": symbol.name, "snapshot": snapshot}


def get_serialized_events():
    tracer_events = []
    for event in trace.events:
        event_dict = attr.asdict(event)
        for key, val in event_dict.items():
            if type(val) == Symbol:
                event_dict[key] = serialize_symbol(val)
            elif type(val) == list:
                event_dict[key] = sorted(
                    [serialize_symbol(sym) for sym in val if type(sym) == Symbol],
                    key=lambda x: x["name"],
                )
        event_dict["__class__"] = event.__class__.__name__
        tracer_events.append(event_dict)
    return tracer_events


@pytest.fixture(scope="function")
def check_tracer_events():
    yield

    tracer_events = get_serialized_events()

    golden_filepath = f"test/data/{python_version}/{trace.frame.frame_name}.json"
    golden_tracer_events = get_golden_data(golden_filepath, "tracer.events")
    if golden_tracer_events is None:
        update_golden_data(golden_filepath, "tracer.events", tracer_events)
    else:
        assert tracer_events == golden_tracer_events, json.dumps(
            tracer_events, indent=4
        )


@pytest.fixture
def check_response(request):
    with responses.RequestsMock() as resp:
        resp.add(
            responses.POST,
            f"http://localhost:{trace.rpc_client.port}/frame",
            status=200,
            content_type="application/octet-stream",
        )
        yield

        response = msgpack.unpackb(resp.calls[0].request.body)
        frame_name = response["metadata"]["frame_name"]

        # Don't check request body on Windows because it has a different format.
        if get_os_type() == "windows" and frame_name in {"test_numpy", "test_pandas"}:
            return

        golden_filepath = f"test/data/{python_version}/{frame_name}.json"
        golden_response = get_golden_data(golden_filepath, "response")
        if golden_response is None:
            update_golden_data(golden_filepath, "response", response)
        else:
            assert response == golden_response, json.dumps(response, indent=4)


@pytest.fixture
def check_golden_file(check_tracer_events, check_response):
    yield
