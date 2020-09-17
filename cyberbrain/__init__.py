# Users shouldn't need to instantiate a Tracer object themselves.
from .tracer import Tracer as _Tracer
from .basis import (
    Binding,
    InitialValue,
    Deletion,
    Mutation,
    Symbol,
    Loop,
    JumpBackToLoopStart,
)

# Test only
from .utils import pprint

trace = tracer = _Tracer()
