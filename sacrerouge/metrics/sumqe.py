import argparse
import json
import os
from overrides import overrides
from subprocess import Popen, PIPE
from typing import List

from sacrerouge.commands import Subcommand
from sacrerouge.common import DATA_ROOT, TemporaryDirectory
from sacrerouge.io import JsonlWriter
from sacrerouge.data import MetricsDict
from sacrerouge.data.fields import SummaryField
from sacrerouge.data.types import SummaryType
from sacrerouge.metrics import Metric


@Metric.register('sum-qe')
class SumQE(Metric):
    def __init__(self,
                 model_file: str = f'{DATA_ROOT}/metrics/SumQE/models/multitask_5-duc2006_duc2007.npy',
                 sum_qe_root: str = f'{DATA_ROOT}/metrics/SumQE',
                 environment_name: str = None,
                 verbose: bool = False):
        super().__init__([])
        self.model_file = os.path.abspath(model_file)
        self.sum_qe_root = sum_qe_root
        self.environment_name = environment_name
        self.verbose = verbose

    def _flatten_summary(self, summary: SummaryType) -> str:
        if isinstance(summary, list):
            return ' '.join(summary)
        return summary

    def _run(self, summaries_list: List[List[SummaryType]]) -> List[List[MetricsDict]]:
        with TemporaryDirectory() as temp_dir:
            summaries_file = f'{temp_dir}/summaries.jsonl'
            predictions_file = f'{temp_dir}/predictions.json'

            # Save all of the summaries to a file
            with JsonlWriter(summaries_file) as out:
                for summaries in summaries_list:
                    for summary in summaries:
                        out.write({'summary': self._flatten_summary(summary)})

            commands = [f'cd {self.sum_qe_root}']
            if self.environment_name:
                commands += [f'source activate {self.environment_name}']
            commands += [
                ' '.join([
                    'python', '-m', 'src.BERT_experiments.predict',
                    summaries_file,
                    self.model_file,
                    predictions_file
                ])
            ]

            redirect = None if self.verbose else PIPE
            process = Popen(' && '.join(commands), stdout=redirect, stderr=redirect, shell=True)
            stdout, stderr = process.communicate()

            predictions = json.loads(open(predictions_file, 'r').read())

            index = 0
            metrics_lists = []
            for summaries in summaries_list:
                metrics_lists.append([])
                for summary in summaries:
                    preds = predictions[index]
                    metrics_lists[-1].append(MetricsDict({
                        'SumQE': {
                            'Q1': preds[0],
                            'Q2': preds[1],
                            'Q3': preds[2],
                            'Q4': preds[3],
                            'Q5': preds[4]
                        }
                    }))
                    index += 1

            return metrics_lists

    def score_multi_all(self, summaries_list: List[List[SummaryField]]) -> List[List[MetricsDict]]:
        # Just take the summaries themselves, not the fields
        summaries_list = [[field.summary for field in fields] for fields in summaries_list]
        return self._run(summaries_list)


class SumQESetupSubcommand(Subcommand):
    @overrides
    def add_subparser(self, parser: argparse._SubParsersAction):
        self.parser = parser.add_parser('sum-qe')
        self.parser.add_argument('--download-2005-2006-model', action='store_true')
        self.parser.add_argument('--download-2005-2007-model', action='store_true')
        self.parser.add_argument('--download-2006-2007-model', action='store_true')
        self.parser.set_defaults(subfunc=self.run)

    @overrides
    def run(self, args):
        commands = [
            f'mkdir -p {DATA_ROOT}/metrics',
            f'cd {DATA_ROOT}/metrics',
            f'git clone https://github.com/danieldeutsch/SumQE',
            f'mkdir -p SumQE/models'
        ]
        if args.download_2005_2006_model:
            commands.append('wget https://danieldeutsch.s3.amazonaws.com/sacrerouge/metrics/SumQE/models/multitask_5-duc2005_duc2006.npy -O SumQE/models/multitask_5-duc2005_duc2006.npy')
        if args.download_2005_2007_model:
            commands.append('wget https://danieldeutsch.s3.amazonaws.com/sacrerouge/metrics/SumQE/models/multitask_5-duc2005_duc2007.npy -O SumQE/models/multitask_5-duc2005_duc2007.npy')
        if args.download_2006_2007_model:
            commands.append('wget https://danieldeutsch.s3.amazonaws.com/sacrerouge/metrics/SumQE/models/multitask_5-duc2006_duc2007.npy -O SumQE/models/multitask_5-duc2006_duc2007.npy')

        command = ' && '.join(commands)

        process = Popen(command, shell=True)
        process.communicate()

        if process.returncode == 0:
            print('SumQE setup success')
        else:
            print('SumQE setup failure')
