from cyberbrain import Tracer


def run_loop():
    tracer = Tracer()
    tracer.start()

    for i in range(2):
        for j in range(2):
            a = i + j

    tracer.stop()


if __name__ == "__main__":
    run_loop()
