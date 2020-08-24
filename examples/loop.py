from birdseye import eye


@eye
def f():
    for i in range(10):
        print(i)

    for i, j in enumerate(range(5)):
        for k in range(5):
            print(i, j)

    x = [i for i in range(10)]

    return 1


f()
