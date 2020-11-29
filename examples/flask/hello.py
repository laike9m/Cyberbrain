from flask import Flask

from cyberbrain import trace

app = Flask(__name__)


# Adding @trace here won't work.
@app.route("/")
@trace
def hello_world():
    f()
    x = [1, 2, 3]
    return "Hello, World!"


def f():
    a = 1
    b = a
