import argparse
from overrides import overrides

from sacrerouge.datasets.multiling.multiling2013 import mds, sds
from sacrerouge.commands import Subcommand
from sacrerouge.common.util import download_file_from_google_drive


class MultiLing2013Subcommand(Subcommand):
    @overrides
    def add_subparser(self, parser: argparse._SubParsersAction):
        description = 'Setup the MultiLing 2013 dataset'
        self.parser = parser.add_parser('multiling2013', description=description, help=description)
        self.parser.add_argument(
            'output_dir',
            type=str,
            help='The directory where the data should be saved'
        )
        self.parser.add_argument(
            '--mds-documents-zip',
            type=str,
            help='The path to "SourceTextsV2b.zip"'
        )
        self.parser.add_argument(
            '--mds-model-summaries-zip',
            type=str,
            help='The path to "ModelSummaries- 20130605.zip"'
        )
        self.parser.set_defaults(subfunc=self.run)

    def _notify_about_license(self):
        print('This dataset is distributed by MultiLing 2013. If you use this dataset, please refer to their '
              'website (http://multiling.iit.demokritos.gr/pages/view/662/multiling-2013) '
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
        # http://multiling.iit.demokritos.gr/pages/view/1571/datasets
        tar_path = f'{args.output_dir}/multilingpilot2013.tar.bz2'
        download_file_from_google_drive('0B31rakzMfTMZRTZiM29UR3VxYmc', tar_path)
        sds.setup(tar_path, f'{args.output_dir}/sds')

        # MDS data is password protected, so the user must provide the data
        if args.mds_documents_zip is None or args.mds_model_summaries_zip is None:
            print('Skipping setting up MDS task because either documenxts or model summaries zip not provided')
        else:
            mds.setup(args.mds_documents_zip, args.mds_model_summaries_zip, f'{args.output_dir}/mds')