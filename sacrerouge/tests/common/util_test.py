import unittest

from sacrerouge.common.util import command_exists


class TestUtil(unittest.TestCase):
    def test_command_exists(self):
        assert command_exists('python')
        assert not command_exists('asdfasd')
