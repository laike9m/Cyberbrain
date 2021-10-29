from cyberbrain import InitialValue, Binding, Symbol


def test_mutation(tracer, check_golden_file):
    text = "AAAA"

    tracer.start()

    lower_text = text.lower()  # Test this line does not emit a mutation of `text`.

    tracer.stop()
