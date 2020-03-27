import argparse
from overrides import overrides

from sacrerouge.datasets.chaganty2018 import setup
from sacrerouge.commands import Subcommand


class Chaganty2018Subcommand(Subcommand):
    @overrides
    def add_subparser(self, parser: argparse._SubParsersAction):
        self.parser = parser.add_parser('chaganty2018')
        self.parser.add_argument('output_dir')
        self.parser.set_defaults(subfunc=self.run)

    @overrides
    def run(self, args):
        setup.setup(args.output_dir)
