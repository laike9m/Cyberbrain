def test_aaa(tracer, rpc_stub):
    tracer.start_tracing()
    for i in range(2):
        if i == 1:
            break
    tracer.stop_tracing()
