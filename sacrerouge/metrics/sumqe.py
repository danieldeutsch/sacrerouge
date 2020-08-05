import argparse
import json
import logging
import os
from overrides import overrides
from subprocess import Popen, PIPE
from typing import List

from sacrerouge.commands import Subcommand
from sacrerouge.common import DATA_ROOT, TemporaryDirectory
from sacrerouge.io import JsonlWriter
from sacrerouge.data import MetricsDict
from sacrerouge.data.types import SummaryType
from sacrerouge.metrics import Metric, ReferenceFreeMetric

logger = logging.getLogger(__name__)


@Metric.register('sum-qe')
class SumQE(ReferenceFreeMetric):
    def __init__(self,
                 model_file: str = f'{DATA_ROOT}/metrics/SumQE/models/multitask_5-duc2006_duc2007.npy',
                 sum_qe_root: str = f'{DATA_ROOT}/metrics/SumQE',
                 python_binary: str = 'python',
                 verbose: bool = False):
        super().__init__([])
        self.model_file = os.path.abspath(model_file)
        self.sum_qe_root = sum_qe_root
        self.python_binary = python_binary
        self.verbose = verbose

        if not os.path.exists(model_file):
            raise Exception(f'Path "{model_file}" does not exist. Have you setup SumQE?')
        if not os.path.exists(sum_qe_root):
            raise Exception(f'Path "{sum_qe_root}" does not exist. Have you setup SumQE?')

    def _flatten_summary(self, summary: SummaryType) -> str:
        if isinstance(summary, list):
            return ' '.join(summary)
        return summary

    def _run(self, summaries_list: List[List[SummaryType]]) -> List[List[MetricsDict]]:
        with TemporaryDirectory() as temp_dir:
            summaries_file = f'{temp_dir}/summaries.jsonl'
            predictions_file = f'{temp_dir}/predictions.json'

            # Save all of the summaries to a file, keeping track of the indices
            # that are empty summaries
            empty_summaries = set()
            with JsonlWriter(summaries_file) as out:
                index = 0
                for summaries in summaries_list:
                    for summary in summaries:
                        summary = self._flatten_summary(summary)
                        if len(summary) > 0:
                            out.write({'summary': summary})
                        else:
                            empty_summaries.add(index)
                        index += 1

            commands = [
                f'cd {self.sum_qe_root}',
                ' '.join([
                    self.python_binary, '-m', 'src.BERT_experiments.predict',
                    summaries_file,
                    self.model_file,
                    predictions_file
                ])
            ]
            command = ' && '.join(commands)

            logger.info(f'Running SumQE command: "{command}"')
            redirect = None if self.verbose else PIPE
            process = Popen(command, stdout=redirect, stderr=redirect, shell=True)
            stdout, stderr = process.communicate()

            predictions = json.loads(open(predictions_file, 'r').read())

            index = 0
            output_index = 0
            metrics_lists = []
            for summaries in summaries_list:
                metrics_lists.append([])
                for _ in summaries:
                    if index in empty_summaries:
                        metrics_lists[-1].append(MetricsDict({
                            'SumQE': {
                                'Q1': 0.0,
                                'Q2': 0.0,
                                'Q3': 0.0,
                                'Q4': 0.0,
                                'Q5': 0.0
                            }
                        }))
                    else:
                        preds = predictions[output_index]
                        metrics_lists[-1].append(MetricsDict({
                            'SumQE': {
                                'Q1': preds[0],
                                'Q2': preds[1],
                                'Q3': preds[2],
                                'Q4': preds[3],
                                'Q5': preds[4]
                            }
                        }))
                        output_index += 1
                    index += 1

            return metrics_lists

    def score_multi_all(self, summaries_list: List[List[SummaryType]]) -> List[List[MetricsDict]]:
        return self._run(summaries_list)


class SumQESetupSubcommand(Subcommand):
    @overrides
    def add_subparser(self, parser: argparse._SubParsersAction):
        description = 'Setup the Sum-QE metric'
        self.parser = parser.add_parser('sum-qe', description=description, help=description)
        self.parser.add_argument(
            '--download-2005-2006-model',
            action='store_true',
            help='Indicates that the model trained on DUC 2005 and 2006 should be downloaded'
        )
        self.parser.add_argument(
            '--download-2005-2007-model',
            action='store_true',
            help='Indicates that the model trained on DUC 2005 and 2007 should be downloaded'
        )
        self.parser.add_argument(
            '--download-2006-2007-model',
            action='store_true',
            help='Indicates that the model trained on DUC 2006 and 2007 should be downloaded'
        )
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
