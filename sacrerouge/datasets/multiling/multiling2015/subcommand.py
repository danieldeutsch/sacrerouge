import argparse
from overrides import overrides

from sacrerouge.datasets.multiling.multiling2015 import mds, sds, sds_metrics
from sacrerouge.commands import DatasetSetupSubcommand
from sacrerouge.common.util import download_file_from_google_drive


@DatasetSetupSubcommand.register('multiling2015')
class MultiLing2015Subcommand(DatasetSetupSubcommand):
    @overrides
    def add_subparser(self, parser: argparse._SubParsersAction):
        description = 'Setup the MultiLing 2015 dataset'
        self.parser = parser.add_parser('multiling2015', description=description, help=description)
        self.parser.add_argument(
            'output_dir',
            type=str,
            help='The directory where the data should be saved'
        )
        self.parser.add_argument(
            '--train-zip',
            type=str,
            help='The path to the "TrainingData2015-20150314.zip" file'
        )
        self.parser.add_argument(
            '--test-zip',
            type=str,
            help='The path to the "SourceTextsV2b-20150214.zip" file'
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

        # The SDS metrics file was provided by John Conroy
        eval_tar_path = f'{args.output_dir}/Evaluation_MultiLing2015_MSS.tgz'
        download_file_from_google_drive('1j_jV9JAc0t_EulCUMH7Y-dQSpqD9BpFd', eval_tar_path)
        sds_metrics.setup(eval_tar_path, f'{args.output_dir}/sds')

        # The MDS data is password protected, so the user must provide the zips
        if not all([args.train_zip, args.test_zip]):
            print('Skipping setting up MDS data because either the training or testing zip is missing')
        else:
            mds.setup(args.train_zip, args.test_zip, f'{args.output_dir}/mds')