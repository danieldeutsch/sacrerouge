import argparse
from overrides import overrides

from sacrerouge.datasets.duc_tac.tac2011 import metrics, pyramids, task1
from sacrerouge.commands import Subcommand


class TAC2011Subcommand(Subcommand):
    @overrides
    def add_subparser(self, parser: argparse._SubParsersAction):
        description = 'Setup the TAC 2011 dataset'
        self.parser = parser.add_parser('tac2011', description=description, help=description)
        self.parser.add_argument(
            'gigaword_root',
            type=str,
            help='The path to the Gigaword root (LDC2011T07/gigaword_eng_5)'
        )
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
        task1.setup(args.gigaword_root, args.data_root, args.output_dir)
        metrics.setup(args.data_root, args.output_dir)
        pyramids.setup(args.data_root, args.output_dir)