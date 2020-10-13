import argparse
import unittest

from sacrerouge.common.testing.util import command_exists


class TestUtil(unittest.TestCase):
    def test_command_exists(self):
        parser = argparse.ArgumentParser()
        assert command_exists(parser, ['test']) is False

        subparsers = parser.add_subparsers()
        assert command_exists(parser, ['test']) is False

        parser_A = subparsers.add_parser('A')
        parser_B = subparsers.add_parser('B')
        assert command_exists(parser, ['A'])
        assert command_exists(parser, ['B'])
        assert not command_exists(parser, ['C'])
        assert not command_exists(parser, ['B', 'C'])

        subparsers_B = parser_B.add_subparsers()
        parser_C = subparsers_B.add_parser('C')
        assert command_exists(parser, ['B', 'C'])
        assert not command_exists(parser, ['B', 'D'])