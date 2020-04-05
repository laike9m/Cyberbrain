"""Just a hello world."""

import unittest

import cyberbrain

cyberbrain.init()
x = "hello world"
y = x
cyberbrain.register()


class HellowWorldTest(unittest.TestCase):
    def test_get_logger(self):
        logger = cyberbrain._get_logger()


if __name__ == "__main__":
    unittest.main()
