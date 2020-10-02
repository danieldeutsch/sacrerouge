import unittest

import sacrerouge


class TestVersion(unittest.TestCase):
    def test_version_exists(self):
        assert sacrerouge.__version__