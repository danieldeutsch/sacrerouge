import argparse
from overrides import overrides

from sacrerouge.datasets.multiling.multiling2017 import sds, sds_metrics
from sacrerouge.commands import DatasetSetupSubcommand
from sacrerouge.common.util import download_file_from_google_drive


@DatasetSetupSubcommand.register('multiling2017')
class MultiLing2017Subcommand(DatasetSetupSubcommand):
    @overrides
    def add_subparser(self, parser: argparse._SubParsersAction):
        description = 'Setup the MultiLing 2017 dataset'
        self.parser = parser.add_parser('multiling2017', description=description, help=description)
        self.parser.add_argument(
            'output_dir',
            type=str,
            help='The directory where the data should be saved'
        )
        self.parser.set_defaults(subfunc=self.run)

    def _notify_about_license(self):
        print('This dataset is distributed by MultiLing 2017. If you use this dataset, please refer to their '
              'website (http://multiling.iit.demokritos.gr/pages/view/1616/multiling-2017)'
              'for instructions on proper attribution.')
        print()
        response = input('Continue? [y/n]: ')
        if response.lower() != 'y':
            exit()

    @overrides
    def run(self, args):
        self._notify_about_license()

        # Link provided by John Conroy
        data_path = f'{args.output_dir}/2017_test_data.tgz'
        download_file_from_google_drive('1dQfEYzJokm0es3xFHJG1J3crBAYU5zTp', data_path)

        eval_path = f'{args.output_dir}/EvaluationML2017.tgz'
        download_file_from_google_drive('1pK7Df5gum5mwC0zYie5mCjqDdqLLmM1j', eval_path)

        sds.setup(data_path, eval_path, f'{args.output_dir}/sds')
        sds_metrics.setup(eval_path, f'{args.output_dir}/sds')
