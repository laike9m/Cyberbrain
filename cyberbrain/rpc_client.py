"""
Server that serves requests from UI (VSC as of now).
"""

from __future__ import annotations

import attr
import msgpack
import requests

from .basis import (
    Event,
    InitialValue,
    Binding,
    Mutation,
    Deletion,
    Return,
    JumpBackToLoopStart,
)
from .frame import Frame


def _get_event_sources_uids(event: Event, frame: Frame) -> Optional[list[str]]:
    """Do tracing.

    Given code like:

    x = "foo"
    y = "bar"
    x, y = y, x

    which has events:
        Binding(target="x", value="foo", id='1'),
        Binding(target="y", value="bar", id='3'),
        Binding(target="x", value="bar", sources={"y"}, id='2'),
        Binding(target="y", value="foo", sources={"x"}, id='4'),

    Tracing result would be:

        {
            '2': ['3'],
            '4': ['1']
        }

    However if we use the most naive method, which look at all identifiers in
    sources and find its predecessor event, we would end up with:

        {
            '2': ['3'],
            '4': ['2']  # Wrong!
        }

    Here, the value assigned to `y` is "foo", but because on the bytecode level,
    `x = y` happens before `y = x`, so the program thinks y's source is
     Mutation(target="x", value="bar", sources={"y"}, id='2').

    To solve this issue, we store snapshot in source's symbol. So by looking at the
    snapshot, we know it points to the Binding(target="x", value="foo", id='1') event,
    not the mutation event. For mutation events, we update the snapshot in symbols that
    are still on value stack, because it needs to point to the mutation event since the
    object on value stack (if any) has changed. For binding events, because the object
    on value stack is not changed, therefore no need to update snapshots.
    """

    event_type = type(event)

    if event_type in {InitialValue, Deletion, JumpBackToLoopStart}:
        return

    assert event_type in {Binding, Mutation, Return}

    if not event.sources:
        return

    sources_uids = []
    for source in sorted(event.sources, key=lambda x: x.name):
        source_event_index = source.snapshot.events_pointer[source.name]
        source_event = frame.identifier_to_events[source.name][source_event_index]
        sources_uids.append(source_event.id)

    return sources_uids


class RpcClient:
    def __init__(self, rpc_server_port=1989):
        self.port = rpc_server_port

    def send_frame(self, frame: Frame):
        frame_data: dict[str, Any] = {
            "metadata": frame.metadata,
            "identifiers": list(frame.identifier_to_events.keys()),
            "loops": [
                {
                    "startOffset": loop.start_offset,
                    "endOffset": loop.end_offset,
                    "startLineno": loop.start_lineno,
                }
                for loop in frame.loops.values()
            ],
            "events": [],
            "tracingResult": {},
        }
        for event in frame.events:
            event_dict = attr.asdict(
                event,
                filter=lambda field, _: False if field.name == "sources" else True,
                value_serializer=event.value_serializer,
            )
            # We have to explicitly write the type name because Js does not know it.
            event_dict["type"] = type(event).__name__
            frame_data["events"].append(event_dict)
            event_ids = _get_event_sources_uids(event, frame)
            if event_ids:
                frame_data["tracingResult"][event.id] = event_ids

        requests.post(
            f"http://localhost:{self.port}/frame",
            data=msgpack.packb(frame_data),
            headers={"Content-Type": "application/octet-stream"},
        )
