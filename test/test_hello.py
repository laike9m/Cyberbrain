from cyberbrain import Creation, Mutation


def test_hello(tracer, rpc_stub):
    tracer.init()
    x = "hello world"  # LOAD_CONST, STORE_FAST
    y = x  # LOAD_FAST, STORE_FAST
    x, y = y, x  # ROT_TWO or BUILD_TUPLE. I don't know how Python compiler decides it.
    tracer.register()

    assert tracer.events == {
        "x": [
            Creation(target="x", value="hello world", lineno=6),
            Mutation(target="x", value="hello world", sources={"y"}, lineno=8),
        ],
        "y": [
            Creation(target="y", value="hello world", sources={"x"}, lineno=7),
            Mutation(target="y", value="hello world", sources={"x"}, lineno=8),
        ],
    }

    from cyberbrain.generated import communication_pb2
    from google.protobuf import text_format

    assert rpc_stub.GetFrame(
        communication_pb2.FrameLocater(frame_name="test_hello")
    ) == text_format.Parse(
        """
        filename: "cb-experimental/test/test_hello.py"
        events {
          key: "x"
          value {
            events {
              creation {
                uid: "test_hello:1"
                filename: "cb-experimental/test/test_hello.py"
                lineno: 6
                target: "x"
                value: "hello world"
              }
            }
            events {
              mutation {
                uid: "test_hello:4"
                filename: "cb-experimental/test/test_hello.py"
                lineno: 8
                target: "x"
                value: "hello world"
                delta: "{}"
                sources: "y"
              }
            }
          }
        }
        events {
          key: "y"
          value {
            events {
              creation {
                uid: "test_hello:3"
                filename: "cb-experimental/test/test_hello.py"
                lineno: 7
                target: "y"
                value: "hello world"
                sources: "x"
              }
            }
            events {
              mutation {
                uid: "test_hello:5"
                filename: "cb-experimental/test/test_hello.py"
                lineno: 8
                target: "y"
                value: "hello world"
                delta: "{}"
                sources: "x"
              }
            }
          }
        }
        """,
        communication_pb2.Frame(),
    )
