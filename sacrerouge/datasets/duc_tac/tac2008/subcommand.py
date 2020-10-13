import argparse
from overrides import overrides

from sacrerouge.datasets.duc_tac.tac2008 import metrics, pyramids, task1
from sacrerouge.commands import DatasetSetupSubcommand


@DatasetSetupSubcommand.register('tac2008')
class TAC2008Subcommand(DatasetSetupSubcommand):
    @overrides
    def add_subparser(self, parser: argparse._SubParsersAction):
        description = 'Setup the TAC 2008 dataset'
        self.parser = parser.add_parser('tac2008', description=description, help=description)
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
        task1.setup(args.data_root, args.output_dir)
        metrics.setup(args.data_root, args.output_dir)
        pyramids.setup(args.data_root, args.output_dir)
