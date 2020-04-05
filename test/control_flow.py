from _test_base import TestBase

import cyberbrain

cyberbrain.init()

a = []
if a:
    x = 1
else:
    x = 2

cyberbrain.register()


class ControlFlowTest(TestBase):
    def test_if(self):
        self.assertEqual(self.logger.mutations, [("a", []), ("x", 2)])


if __name__ == "__main__":
    unittest.main()
