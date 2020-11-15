"""
Server that serves requests from UI (VSC as of now).
"""

from __future__ import annotations

import grpc

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
from .generated import communication_pb2
from .generated import communication_pb2_grpc


def _transform_event_to_proto(event: Event) -> communication_pb2.Event:
    event_proto = communication_pb2.Event()
    if isinstance(event, InitialValue):
        event_proto.initial_value.CopyFrom(
            communication_pb2.InitialValue(
                id=event.uid,
                filename=event.filename,
                lineno=event.lineno,
                index=event.index,
                offset=event.offset,
                target=event.target.name,
                value=event.value,
                repr=event.repr,
            )
        )
    elif isinstance(event, Binding):
        event_proto.binding.CopyFrom(
            communication_pb2.Binding(
                id=event.uid,
                filename=event.filename,
                lineno=event.lineno,
                index=event.index,
                offset=event.offset,
                target=event.target.name,
                value=event.value,
                repr=event.repr,
                # Sorted to make result deterministic.
                sources=sorted(source.name for source in event.sources),
            )
        )
    elif isinstance(event, Mutation):
        event_proto.mutation.CopyFrom(
            communication_pb2.Mutation(
                id=event.uid,
                filename=event.filename,
                lineno=event.lineno,
                index=event.index,
                offset=event.offset,
                target=event.target.name,
                value=event.value,
                repr=event.repr,
                sources=sorted(source.name for source in event.sources),
            )
        )
    elif isinstance(event, Deletion):
        event_proto.deletion.CopyFrom(
            communication_pb2.Deletion(
                id=event.uid,
                filename=event.filename,
                lineno=event.lineno,
                index=event.index,
                offset=event.offset,
                target=event.target.name,
            )
        )
    elif isinstance(event, Return):
        getattr(event_proto, "return").CopyFrom(
            communication_pb2.Return(
                id=event.uid,
                filename=event.filename,
                lineno=event.lineno,
                index=event.index,
                offset=event.offset,
                value=event.value,
                repr=event.repr,
                sources=sorted(source.name for source in event.sources),
            )
        )
    elif isinstance(event, JumpBackToLoopStart):
        event_proto.jump_back_to_loop_start.CopyFrom(
            communication_pb2.JumpBackToLoopStart(
                id=event.uid,
                filename=event.filename,
                lineno=event.lineno,
                index=event.index,
                offset=event.offset,
                jump_target=event.jump_target,
            )
        )

    return event_proto


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
        sources_uids.append(source_event.uid)

    return sources_uids


class RpcClient:
    def __init__(self):
        self.port = 1989
        self.channel = grpc.insecure_channel(f"localhost:{self.port}")
        self.stub = communication_pb2_grpc.CommunicationStub(self.channel)

    def send_frame(self, frame: Frame):
        frame_proto = communication_pb2.Frame(
            metadata=communication_pb2.FrameLocater(
                frame_id=frame.frame_id,
                frame_name=frame.frame_name,
                filename=frame.filename,
            ),
            identifiers=list(frame.identifier_to_events.keys()),
            loops=[
                communication_pb2.Loop(
                    start_offset=loop.start_offset,
                    end_offset=loop.end_offset,
                    start_lineno=loop.start_lineno,
                )
                for loop in frame.loops.values()
            ],
        )

        for event in frame.events:
            frame_proto.events.append(_transform_event_to_proto(event))
            event_ids = _get_event_sources_uids(event, frame)
            if event_ids:
                frame_proto.tracing_result[event.uid].event_ids[:] = event_ids

        self.stub.SendFrame(frame_proto)
