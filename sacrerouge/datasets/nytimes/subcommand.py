import argparse
from overrides import overrides

from sacrerouge.datasets.nytimes import setup
from sacrerouge.commands import DatasetSetupSubcommand


@DatasetSetupSubcommand.register('nytimes')
class NYTimesSubcommand(DatasetSetupSubcommand):
    @overrides
    def add_subparser(self, parser: argparse._SubParsersAction):
        description = 'Setup the NYTimes dataset'
        self.parser = parser.add_parser('nytimes', description=description, help=description)
        self.parser.add_argument(
            'ldc2008t19_tgz',
            type=str,
            help='The tgz of the LDC2008T19 NYTimes dataset, "nyt_corpus_LDC2008T19.tgz"'
        )
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
        setup.setup(args.ldc2008t19_tgz, args.output_dir, args.force)
