import unittest
import cyberbrain


class TestBase(unittest.TestCase):
    def setUp(self):
        self.logger = cyberbrain._get_logger()

    def tearDown(self):
        cyberbrain._clear_logger()
