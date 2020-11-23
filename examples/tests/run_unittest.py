import unittest

from cyberbrain import trace


class TestStringMethods(unittest.TestCase):
    @trace
    def test_split(self):
        self.assertEqual("foo".upper(), "FOO")

        s = "hello world"
        self.assertEqual(s.split(), ["hello", "world"])
        # check that s.split fails when the separator is not a string
        with self.assertRaises(TypeError):
            s.split(2)


if __name__ == "__main__":
    unittest.main()
