import argparse
from overrides import overrides

from sacrerouge.datasets.multiling.multiling2015 import sds
from sacrerouge.commands import Subcommand
from sacrerouge.common.util import download_file_from_google_drive


class MultiLing2015Subcommand(Subcommand):
    @overrides
    def add_subparser(self, parser: argparse._SubParsersAction):
        description = 'Setup the MultiLing 2015 dataset'
        self.parser = parser.add_parser('multiling2015', description=description, help=description)
        self.parser.add_argument(
            'output_dir',
            type=str,
            help='The directory where the data should be saved'
        )
        self.parser.set_defaults(subfunc=self.run)

    def _notify_about_license(self):
        print('This dataset is distributed by MultiLing 2015. If you use this dataset, please refer to their '
              'website (http://multiling.iit.demokritos.gr/pages/view/1516/multiling-2015) '
              'for instructions on proper attribution.')
        print()
        response = input('Continue? [y/n]: ')
        if response.lower() != 'y':
            exit()

    @overrides
    def run(self, args):
        self._notify_about_license()

        # Download the dataset so each individual setup does not need
        # to repeat this. The dataset comes from
        # http://multiling.iit.demokritos.gr/pages/view/1532/task-mss-single-document-summarization-data-and-information
        tar_path = f'{args.output_dir}/multilingMss2015Eval.tar.gz'
        download_file_from_google_drive('0B31rakzMfTMZa0ZIcmgzREstcVE', tar_path)

        sds.setup(tar_path, f'{args.output_dir}/sds')
