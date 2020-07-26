"""
Server that serves requests from UI (VSC as of now).
"""

from __future__ import annotations

import queue
from concurrent import futures
from threading import Timer

import grpc
import jsonpickle

from . import utils
from .basis import Event, InitialValue, Binding, Mutation, Deletion
from .frame_tree import FrameTree
from .generated import communication_pb2
from .generated import communication_pb2_grpc


def transform_event_to_proto(event: Event) -> communication_pb2.Event:
    event_proto = communication_pb2.Event()
    if isinstance(event, InitialValue):
        event_proto.initial_value.CopyFrom(
            communication_pb2.InitialValue(
                uid=event.uid,
                filename=event.filename,
                lineno=event.lineno,
                target=event.target.name,
                value=utils.to_json(event.value),
            )
        )
    elif isinstance(event, Binding):
        event_proto.binding.CopyFrom(
            communication_pb2.Binding(
                uid=event.uid,
                filename=event.filename,
                lineno=event.lineno,
                target=event.target.name,
                value=utils.to_json(event.value),
                # Sorted to make result deterministic.
                sources=sorted(source.name for source in event.sources),
            )
        )
    elif isinstance(event, Mutation):
        event_proto.mutation.CopyFrom(
            communication_pb2.Mutation(
                uid=event.uid,
                filename=event.filename,
                lineno=event.lineno,
                target=event.target.name,
                value=utils.to_json(event.value),
                delta=jsonpickle.encode(event.delta.to_dict(), unpicklable=False),
                sources=sorted(source.name for source in event.sources),
            )
        )
    elif isinstance(event, Deletion):
        event_proto.deletion.CopyFrom(
            communication_pb2.Deletion(
                uid=event.uid,
                filename=event.filename,
                lineno=event.lineno,
                target=event.target.name,
            )
        )

    return event_proto


class CyberbrainCommunicationServicer(communication_pb2_grpc.CommunicationServicer):
    # Queue that stores state to be published to VSC extension.
    state_queue = queue.Queue()

    def SyncState(self, request, context):
        print(f"Received request SyncState: {type(request)} {request}")
        yield communication_pb2.State(status=communication_pb2.State.SERVER_READY)
        Timer(
            5,  # seconds
            lambda: CyberbrainCommunicationServicer.state_queue.put(
                # Simulates when program hits cyberbrain.register().
                communication_pb2.State(
                    status=communication_pb2.State.EXECUTION_COMPLETE
                )
            ),
        ).start()
        while True:
            yield self.state_queue.get()  # block forever.

    def FindFrames(self, request, context):
        frames = FrameTree.find_frames(request)
        raise NotImplementedError

    def GetFrame(
        self, request: communication_pb2.FrameLocater, context
    ) -> communication_pb2.Frame:
        # TODO: return tracing result.
        print(f"Received request GetFrame: {type(request)} {request}")
        frame = FrameTree.get_frame(request.frame_name)
        frame_proto = communication_pb2.Frame(filename=frame.filename)
        for identifier, events in frame.accumulated_events.items():
            frame_proto.events[identifier].CopyFrom(
                communication_pb2.EventList(
                    events=[transform_event_to_proto(event) for event in events]
                )
            )
        return frame_proto


class Server:
    def __init__(self):
        self._server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
        communication_pb2_grpc.add_CommunicationServicer_to_server(
            CyberbrainCommunicationServicer(), self._server
        )
        self._port = None

    def serve(self, port: int = 50051):
        print(f"Starting grpc server on {port}...")
        self._port = port
        self._server.add_insecure_port(f"[::]:{port}")
        self._server.start()

    def wait_for_termination(self):
        self._server.wait_for_termination()

    def stop(self):
        self._server.stop(grace=None)  # Abort all active RPCs immediately.

    @property
    def port(self):
        return self._port


if __name__ == "__main__":
    server = Server()
    server.serve()
    server.wait_for_termination()
