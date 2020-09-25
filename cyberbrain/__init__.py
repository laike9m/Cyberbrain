# Users shouldn't need to instantiate a Tracer object themselves.
from .tracer import Tracer as _Tracer, TracerFSM as _TracerFSM
from .basis import (
    Binding,
    InitialValue,
    Deletion,
    Mutation,
    Return,
    Symbol,
    Loop,
    JumpBackToLoopStart,
)

# Test only
from .utils import pprint

trace = tracer = _Tracer()
