import argparse
from overrides import overrides

from sacrerouge.datasets.multiling.multiling2019 import eval
from sacrerouge.commands import DatasetSetupSubcommand
from sacrerouge.common.util import download_file_from_google_drive


@DatasetSetupSubcommand.register('multiling2019')
class MultiLing2019Subcommand(DatasetSetupSubcommand):
    @overrides
    def add_subparser(self, parser: argparse._SubParsersAction):
        description = 'Setup the MultiLing 2019 dataset'
        self.parser = parser.add_parser('multiling2019', description=description, help=description)
        self.parser.add_argument(
            'output_dir',
            type=str,
            help='The directory where the data should be saved'
        )
        self.parser.set_defaults(subfunc=self.run)

    def _notify_about_license(self):
        print('This dataset is distributed by MultiLing 2019. If you use this dataset, please refer to their '
              'website (http://multiling.iit.demokritos.gr/pages/view/1644/multiling-2019) '
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
        # The link comes from http://multiling.iit.demokritos.gr/pages/view/1650/task-summary-evaluation
        zip_path = f'{args.output_dir}/summary_eval_v2.zip'
        download_file_from_google_drive('1mRlEoqShJxgxrMJO1VgWlUuuaq_SJayy', zip_path)

        eval.setup(zip_path, args.output_dir)
