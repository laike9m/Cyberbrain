from cyberbrain import trace

@trace
def run_while():
    i = 0
    while (i:= i+1) < 3:
        a = i


run_while()