import unittest

import sacrerouge


class TestVersion(unittest.TestCase):
    def test_version_exists(self):
        # Test to make sure the variable exists and is parsable
        assert sacrerouge.__version__