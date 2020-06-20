import argparse
from overrides import overrides

from sacrerouge.datasets.chaganty2018 import setup
from sacrerouge.commands import Subcommand


class Chaganty2018Subcommand(Subcommand):
    @overrides
    def add_subparser(self, parser: argparse._SubParsersAction):
        description = 'Setup the Chaganty 2018 dataset'
        self.parser = parser.add_parser('chaganty2018', description=description, help=description)
        self.parser.add_argument(
            'output_dir',
            type=str,
            help='The directory where the data should be written'
        )
        self.parser.set_defaults(subfunc=self.run)

    @overrides
    def run(self, args):
        setup.setup(args.output_dir)
