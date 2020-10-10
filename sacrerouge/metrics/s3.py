import argparse
import logging
import os
import shutil
from overrides import overrides
from subprocess import Popen, PIPE
from typing import List

from sacrerouge.commands import Subcommand
from sacrerouge.common import DATA_ROOT, TemporaryDirectory
from sacrerouge.data import MetricsDict
from sacrerouge.data.jackknifers import ReferencesJackknifer
from sacrerouge.data.types import ReferenceType, SummaryType
from sacrerouge.metrics import Metric, ReferenceBasedMetric
from sacrerouge.io import JsonlReader, JsonlWriter

logger = logging.getLogger(__name__)


@Metric.register('s3')
class S3(ReferenceBasedMetric):
    def __init__(self,
                 environment_name: str = None,
                 s3_root: str = f'{DATA_ROOT}/metrics/S3',
                 embeddings_file: str = f'{DATA_ROOT}/metrics/S3/deps.words.bz2',
                 model_dir: str = f'{DATA_ROOT}/metrics/S3/models/en',
                 verbose: bool = True):
        super().__init__(['summary'], ['references'], jackknifer=ReferencesJackknifer())
        self.environment_name = environment_name
        self.s3_root = s3_root
        self.embeddings_file = embeddings_file
        self.model_dir = model_dir
        self.verbose = verbose

        if self.environment_name is not None:
            if 'CONDA_INIT' not in os.environ:
                raise Exception('If `environment_name` is not none, environment variable "CONDA_INIT" must be set to the path to "conda.sh"')

    def _flatten_summaries(self, summaries_list: List[List[SummaryType]]) -> List[List[str]]:
        flattened_list = []
        for summaries in summaries_list:
            flattened_list.append([])
            for summary in summaries:
                if isinstance(summary, list):
                    summary = ' '.join(summary)
                flattened_list[-1].append(summary)
        return flattened_list

    def score_multi_all(self,
                        summaries_list: List[List[SummaryType]],
                        references_list: List[List[ReferenceType]],
                        **kwargs) -> List[List[MetricsDict]]:
        summaries_list = self._flatten_summaries(summaries_list)
        references_list = self._flatten_summaries(references_list)

        logger.info(f'Serializing the summaries and references to a file')
        num_summaries = 0
        with TemporaryDirectory() as temp_dir:
            input_file = f'{temp_dir}/input.jsonl'
            output_file = f'{temp_dir}/output.jsonl'
            with JsonlWriter(input_file) as out:
                for summaries, references in zip(summaries_list, references_list):
                    for summary in summaries:
                        out.write({
                            'summary': summary,
                            'references': references
                        })
                        num_summaries += 1
            logger.info(f'Wrote {num_summaries} (summary, references) pairs')

            commands = [f'cd {self.s3_root}/S3']
            if self.environment_name is not None:
                commands.append(f'. {os.environ["CONDA_INIT"]}')
                commands.append(f'conda activate {self.environment_name}')
            commands.append(f'python2.7 run_batch.py {input_file} {output_file} {self.embeddings_file} {self.model_dir}')
            command = ' && '.join(commands)

            logger.info(f'Running command: "{command}"')
            redirect = None if self.verbose else PIPE
            process = Popen(command, stdout=redirect, stderr=redirect, shell=True)
            process.communicate()

            scores = JsonlReader(output_file).read()
            assert len(scores) == num_summaries

            metrics_list = []
            index = 0
            for summaries in summaries_list:
                metrics_list.append([])
                for _ in summaries:
                    metrics_list[-1].append(MetricsDict({
                        's3': {
                            'pyr': scores[index]['pyr'],
                            'resp': scores[index]['resp'],
                        }
                    }))
                    index += 1
            return metrics_list


class S3SetupSubcommand(Subcommand):
    @overrides
    def add_subparser(self, parser: argparse._SubParsersAction):
        description = 'Setup the S3 metric'
        self.parser = parser.add_parser('s3', description=description, help=description)
        self.parser.add_argument('--force', action='store_true', help='Force setting up the metric again')
        self.parser.set_defaults(subfunc=self.run)

    @overrides
    def run(self, args):
        if args.force and os.path.exists(f'{DATA_ROOT}/metrics/S3'):
            shutil.rmtree(f'{DATA_ROOT}/metrics/S3')

        commands = [
            f'mkdir -p {DATA_ROOT}/metrics',
            f'cd {DATA_ROOT}/metrics',
            f'git clone https://github.com/danieldeutsch/S3',
            f'cd S3',
            f'wget http://u.cs.biu.ac.il/~yogo/data/syntemb/deps.words.bz2'
        ]
        command = ' && '.join(commands)

        process = Popen(command, shell=True)
        process.communicate()

        if process.returncode == 0:
            print('S3 setup success')
        else:
            print('S3 setup failure')
