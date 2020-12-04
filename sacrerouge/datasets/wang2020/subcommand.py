import argparse
from overrides import overrides

from sacrerouge.datasets.wang2020 import setup
from sacrerouge.commands import DatasetSetupSubcommand


@DatasetSetupSubcommand.register('wang2020')
class Wang2020Subcommand(DatasetSetupSubcommand):
    @overrides
    def add_subparser(self, parser: argparse._SubParsersAction):
        description = 'Setup the Wang 2020 dataset'
        self.parser = parser.add_parser('wang2020', description=description, help=description)
        self.parser.add_argument(
            'output_dir',
            type=str,
            help='The directory where the data should be written'
        )
        self.parser.set_defaults(subfunc=self.run)

    @overrides
    def run(self, args):
        setup.setup(args.output_dir)
