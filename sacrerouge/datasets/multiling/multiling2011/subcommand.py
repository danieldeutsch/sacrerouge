import argparse
from overrides import overrides

from sacrerouge.datasets.multiling.multiling2011 import metrics, task
from sacrerouge.commands import Subcommand
from sacrerouge.common.util import download_url_to_file
from sacrerouge.datasets.dataset_subcommand import DatasetSubcommand


class MultiLing2011Subcommand(DatasetSubcommand):
    def __init__(self, cr, command_prefix):
        args = []
        args.append({"name": "output_dir"})
        super().__init__(cr, command_prefix, "multiling2011", args, self.run)
    
    def _notify_about_license(self):
        print('The MultiLing2011 dataset is distributed by the MultiLing Pilot '
              'of Text Analysis Conference 2011 under the Create Commons Attribution 3.0 '
              'Unported License. If you use this dataset, please refer to their '
              'website (http://users.iit.demokritos.gr/~ggianna/TAC2011/MultiLing2011.html) '
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
        # http://multiling.iit.demokritos.gr/file/view/353/tac-2011-multiling-pilot-dataset-all-files-source-texts-human-and-system-summaries-evaluation-data
        data_path = f'{args.output_dir}/PublishedCorpusFileSet.zip'
        download_url_to_file('http://multiling.iit.demokritos.gr/file/download/353', data_path)

        task.setup(data_path, args.output_dir)
        metrics.setup(data_path, args.output_dir)
