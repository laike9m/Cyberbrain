from cyberbrain import trace

@trace
def run_while():
    i = 0
    while i < 2:
        a = i
        i += 1


run_while()