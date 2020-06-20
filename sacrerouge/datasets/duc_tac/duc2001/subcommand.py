import argparse
from overrides import overrides

from sacrerouge.datasets.duc_tac.duc2001 import tasks
from sacrerouge.commands import Subcommand


class DUC2001Subcommand(Subcommand):
    @overrides
    def add_subparser(self, parser: argparse._SubParsersAction):
        description = 'Setup the DUC 2001 dataset'
        self.parser = parser.add_parser('duc2001', description=description, help=description)
        self.parser.add_argument(
            'data_root',
            type=str,
            help='The path to the root of the repository with the DUC/TAC data (https://github.com/danieldeutsch/duc-tac-data)'
        )
        self.parser.add_argument(
            'output_dir',
            type=str,
            help='The directory where the data should be saved'
        )
        self.parser.set_defaults(subfunc=self.run)

    @overrides
    def run(self, args):
        tasks.setup(args.data_root, args.output_dir)
