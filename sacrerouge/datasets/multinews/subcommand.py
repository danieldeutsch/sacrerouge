import argparse
from overrides import overrides

from sacrerouge.datasets.multinews import setup
from sacrerouge.commands import DatasetSetupSubcommand


@DatasetSetupSubcommand.register('multinews')
class MultiNewsSubcommand(DatasetSetupSubcommand):
    @overrides
    def add_subparser(self, parser: argparse._SubParsersAction):
        description = 'Setup the Multi-News dataset'
        self.parser = parser.add_parser('multinews', description=description, help=description)
        self.parser.add_argument(
            'output_dir',
            type=str,
            help='The directory where the data should be written'
        )
        self.parser.add_argument(
            '--force',
            action='store_true',
            help='Force the raw data to be downloaded even if it already exists on file'
        )
        self.parser.set_defaults(subfunc=self.run)

    @overrides
    def run(self, args):
        setup.setup(args.output_dir, args.force)
