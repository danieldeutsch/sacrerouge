import argparse
from overrides import overrides

from sacrerouge.datasets.fabbri2020 import setup
from sacrerouge.commands import DatasetSetupSubcommand


@DatasetSetupSubcommand.register('fabbri2020')
class Fabbri2020Subcommand(DatasetSetupSubcommand):
    @overrides
    def add_subparser(self, parser: argparse._SubParsersAction):
        description = 'Setup the Fabbri 2020 dataset'
        self.parser = parser.add_parser('fabbri2020', description=description, help=description)
        self.parser.add_argument(
            'cnn_tar',
            type=str,
            help='The path to the downloaded tar file from this link: https://drive.google.com/uc?export=download&id=0BwmD_VLjROrfTHk4NFg2SndKcjQ'
        )
        self.parser.add_argument(
            'dailymail_tar',
            type=str,
            help='The path to the downloaded tar file from this link: https://drive.google.com/uc?export=download&id=0BwmD_VLjROrfM1BxdkxVaTY2bWs'
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
        setup.setup(args.cnn_tar, args.dailymail_tar, args.output_dir, args.force)
