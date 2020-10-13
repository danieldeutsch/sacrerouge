import argparse
import logging
import os
from overrides import overrides
from subprocess import Popen, PIPE
from typing import List

from sacrerouge.commands import MetricSetupSubcommand
from sacrerouge.common import DATA_ROOT, TemporaryDirectory
from sacrerouge.data import MetricsDict
from sacrerouge.data.jackknifers import ReferencesJackknifer
from sacrerouge.data.types import ReferenceType, SummaryType
from sacrerouge.metrics import Metric, ReferenceBasedMetric

logger = logging.getLogger(__name__)


@Metric.register('bleurt')
class Bleurt(ReferenceBasedMetric):
    def __init__(self,
                 environment_name: str = None,
                 checkpoint: str = 'bleurt-base-128',
                 bleurt_root: str = f'{DATA_ROOT}/metrics/bleurt',
                 batch_size: int = 100,
                 verbose: bool = False):
        super().__init__(['summary'], ['references'], jackknifer=ReferencesJackknifer())
        self.environment_name = environment_name
        self.checkpoint = checkpoint.lower()
        self.bleurt_root = bleurt_root
        self.batch_size = batch_size
        self.verbose = verbose

        if self.environment_name is not None:
            if 'CONDA_INIT' not in os.environ:
                raise Exception('If `environment_name` is not none, environment variable "CONDA_INIT" must be set to the path to "conda.sh"')

        self.checkpoint_dir = self._maybe_download_checkpoint(self.checkpoint)

    def _maybe_download_checkpoint(self, checkpoint: str) -> str:
        checkpoints_dir = f'{self.bleurt_root}/checkpoints'
        this_checkpoint_dir = f'{checkpoints_dir}/{checkpoint}'
        if not os.path.exists(this_checkpoint_dir):
            commands = [
                f'mkdir -p {checkpoints_dir}',
                f'cd {checkpoints_dir}',
                f'wget https://storage.googleapis.com/bleurt-oss/{checkpoint}.zip',
                f'unzip {checkpoint}.zip'
            ]
            command = ' && '.join(commands)

            logger.info(f'Downloading checkpoint {checkpoint}')
            logger.info(f'Running command "{command}"')
            process = Popen(command, stdout=None, stderr=None, shell=True)
            process.communicate()

        return this_checkpoint_dir

    def score_multi_all(self,
                        summaries_list: List[List[SummaryType]],
                        references_list: List[List[ReferenceType]]) -> List[List[MetricsDict]]:
        with TemporaryDirectory() as temp_dir:
            # Save the summaries to a file. Each file has one summary per line.
            # For multiple references, each reference is used to evaluate the same
            # summary independently, so the system summary is repeated.
            candidate_file = f'{temp_dir}/candidates.txt'
            reference_file = f'{temp_dir}/references.txt'
            score_file = f'{temp_dir}/scores.txt'

            with open(candidate_file, 'w') as out_candidates:
                with open(reference_file, 'w') as out_references:
                    for summaries, references in zip(summaries_list, references_list):
                        for summary in summaries:
                            for reference in references:
                                if isinstance(summary, list):
                                    out_candidates.write(' '.join(summary) + '\n')
                                else:
                                    out_candidates.write(summary + '\n')

                                if isinstance(reference, list):
                                    out_references.write(' '.join(reference) + '\n')
                                else:
                                    out_references.write(reference + '\n')

            # Run through BLEURT
            commands = [f'cd {self.bleurt_root}']
            if self.environment_name is not None:
                commands.append(f'source {os.environ["CONDA_INIT"]}')
                commands.append(f'conda activate {self.environment_name}')
            commands.append(
                f'python -m bleurt.score '
                f'-candidate_file={candidate_file} '
                f'-reference_file={reference_file} '
                f'-bleurt_checkpoint={self.checkpoint_dir} '
                f'-scores_file={score_file} '
                f'-bleurt_batch_size={self.batch_size}'
            )
            command = ' && '.join(commands)

            logger.info(f'Running command: "{command}"')
            redirect = None if self.verbose else PIPE
            process = Popen(command, stdout=redirect, stderr=redirect, shell=True)
            process.communicate()

            # Load the results
            scores = list(map(float, open(score_file, 'r').read().splitlines()))
            metrics_lists = []
            index = 0
            for summaries, references in zip(summaries_list, references_list):
                metrics_lists.append([])
                for _ in summaries:
                    reference_scores = []
                    for _ in references:
                        reference_scores.append(scores[index])
                        index += 1
                    average = sum(reference_scores) / len(reference_scores)
                    max_ = max(reference_scores)
                    metrics_lists[-1].append(MetricsDict({
                        'bleurt': {
                            'average': average,
                            'max': max_
                        }
                    }))
            return metrics_lists


@MetricSetupSubcommand.register('bleurt')
class BleurtSetupSubcommand(MetricSetupSubcommand):
    @overrides
    def add_subparser(self, parser: argparse._SubParsersAction):
        description = 'Setup the BLEURT metric'
        self.parser = parser.add_parser('bleurt', description=description, help=description)
        self.parser.set_defaults(subfunc=self.run)

    @overrides
    def run(self, args):
        commands = [
            f'cd {DATA_ROOT}/metrics',
            f'git clone https://github.com/google-research/bleurt'
        ]
        command = ' && '.join(commands)

        process = Popen(command, shell=True)
        process.communicate()
        if process.returncode == 0:
            # We do not install BLEURT on our own in case the user wants to use a different
            # python environment for the installation
            print(f'In order to finish setting up BLEURT, follow the instructions on the '
                  f'official repository (https://github.com/google-research/bleurt) to install '
                  f'it and verify it is correct via their unit tests. You should pip install it from '
                  f'the sacrerouge directory: {DATA_ROOT}/metrics/bleurt')
        else:
            print('BLEURT setup failure')