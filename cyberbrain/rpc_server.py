"""
Server that serves requests from UI (VSC as of now).
"""

from __future__ import annotations

import queue
from concurrent import futures
from datetime import datetime

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
from .frame_tree import FrameTree
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


class CyberbrainCommunicationServicer(communication_pb2_grpc.CommunicationServicer):
    def __init__(self, state_queue: queue.Queue):
        # Queue that stores state to be published to VSC extension.
        self.state_queue = state_queue

    def SyncState(self, request: communication_pb2.State, context: grpc.RpcContext):
        print(f"{datetime.now().time()} Received SyncState: {type(request)} {request}")

        # Detects RPC termination, sets a sentinel and allows SyncState to return.
        context.add_callback(lambda: self.state_queue.put(-1))

        yield communication_pb2.State(status=communication_pb2.State.SERVER_READY)
        while True:
            state = self.state_queue.get()  # block forever.
            if state == -1:
                print("Client disconnected")
                return
            print(f"Return state: {state}")
            yield state

    def FindFrames(self, request: communication_pb2.CursorPosition, context):
        print(f"{datetime.now().time()} Received FindFrames: {type(request)} {request}")

        return communication_pb2.FrameLocaterList(
            frame_locaters=[
                communication_pb2.FrameLocater(
                    frame_id=frame.frame_id,
                    frame_name=frame.frame_name,
                    filename=frame.filename,
                )
                for frame in FrameTree.find_frames(request)
            ]
        )

    def GetFrame(
        self, frame_locator: communication_pb2.FrameLocater, context
    ) -> communication_pb2.Frame:
        print(f"Received request GetFrame: {type(frame_locator)} {frame_locator}")
        # TODO: Use frame ID for non-test.
        frame = FrameTree.get_frame(frame_locator.frame_name)
        frame_proto = communication_pb2.Frame(metadata=frame_locator)
        frame_proto.identifiers.extend(list(frame.identifier_to_events.keys()))
        frame_proto.loops.extend(
            [
                communication_pb2.Loop(
                    start_offset=loop.start_offset,
                    end_offset=loop.end_offset,
                    start_lineno=loop.start_lineno,
                )
                for loop in frame.loops.values()
            ]
        )
        for event in frame.events:
            frame_proto.events.append(_transform_event_to_proto(event))
            event_ids = _get_event_sources_uids(event, frame)
            if event_ids:
                frame_proto.tracing_result[event.uid].CopyFrom(
                    communication_pb2.EventIDList(event_ids=event_ids)
                )
        return frame_proto


class Server:
    def __init__(self):
        self._server = grpc.server(
            futures.ThreadPoolExecutor(max_workers=5),
            compression=grpc.Compression.Gzip,
        )
        self._state_queue = queue.Queue()
        communication_pb2_grpc.add_CommunicationServicer_to_server(
            CyberbrainCommunicationServicer(state_queue=self._state_queue), self._server
        )
        self._port = None

    def serve(self, port: int = 50051):
        print(f"Starting grpc server on {port}...")
        self._port = port
        self._server.add_insecure_port(f"[::]:{port}")
        self._server.start()

    def wait_for_termination(self):
        self._state_queue.put(
            communication_pb2.State(status=communication_pb2.State.EXECUTION_COMPLETE)
        )
        print("Waiting for termination...")
        self._server.wait_for_termination()

    def stop(self):
        self._server.stop(grace=None)  # Abort all active RPCs immediately.

    @property
    def port(self):
        """Test only. In production the port will is a fixed number 50051."""
        return self._port


if __name__ == "__main__":
    server = Server()
    server.serve()
    server.wait_for_termination()
