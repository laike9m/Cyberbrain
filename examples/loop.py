from cyberbrain import tracer


def run_loop():
    tracer.start()

    for i in range(5):
        a = i
        for j in range(5):
            b = i + j
            for k in range(2):
                c = i + j + k

    tracer.stop()


if __name__ == "__main__":
    run_loop()
