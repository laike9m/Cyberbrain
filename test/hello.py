"""Just a hello world."""

from _test_base import TestBase

import cyberbrain

cyberbrain.init()
x = "hello world"
y = x
cyberbrain.register()


class HellowWorldTest(TestBase):
    def test_hello_world(self):
        self.assertEqual(
            self.logger.mutations, [("x", "hello world"), ("y", "hello world")]
        )


if __name__ == "__main__":
    unittest.main()
