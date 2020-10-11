import argparse
import json
import logging
import os
from overrides import overrides
from subprocess import Popen, PIPE
from typing import List

from sacrerouge.commands import Subcommand
from sacrerouge.common import DATA_ROOT, TemporaryDirectory
from sacrerouge.data import MetricsDict
from sacrerouge.data.types import DocumentType, SummaryType
from sacrerouge.metrics import DocumentBasedMetric, Metric

logger = logging.getLogger(__name__)


@Metric.register('supert')
class SUPERT(DocumentBasedMetric):
    def __init__(self,
                 environment_name: str = None,
                 supert_root: str = f'{DATA_ROOT}/metrics/SUPERT',
                 verbose: bool = False):
        super().__init__(['summary'], ['documents'])
        self.environment_name = environment_name
        self.supert_root = supert_root
        self.verbose = verbose

        if self.environment_name is not None:
            if 'CONDA_INIT' not in os.environ:
                raise Exception('If `environment_name` is not none, environment variable "CONDA_INIT" must be set to the path to "conda.sh"')

    def _save_documents(self, documents: List[List[DocumentType]], output_dir: str) -> None:
        os.makedirs(output_dir)
        for i, document in enumerate(documents):
            with open(f'{output_dir}/{i}.txt', 'w') as out:
                if isinstance(document, list):
                    document = ' '.join(document)
                out.write('<TEXT>\n')
                out.write(document + '\n')
                out.write('</TEXT>\n')

    def _save_summaries(self, summaries: List[List[SummaryType]], output_dir: str) -> None:
        os.makedirs(output_dir)
        for i, summary in enumerate(summaries):
            with open(f'{output_dir}/{i}', 'w') as out:
                if isinstance(summary, list):
                    summary = ' '.join(summary)
                out.write(summary)

    def score_multi_all(self,
                        summaries_list: List[List[SummaryType]],
                        documents_list: List[List[DocumentType]],
                        **kwargs) -> List[List[MetricsDict]]:
        with TemporaryDirectory() as temp_dir:
            input_dir = f'{temp_dir}/input'
            output_file = f'{temp_dir}/output.json'

            logger.info(f'Serializing data to {input_dir}')
            os.makedirs(input_dir)
            for i, (summaries, documents) in enumerate(zip(summaries_list, documents_list)):
                instance_dir = f'{input_dir}/{i}'
                documents_dir = f'{instance_dir}/input_docs'
                summaries_dir = f'{instance_dir}/summaries'

                self._save_documents(documents, documents_dir)
                self._save_summaries(summaries, summaries_dir)

            commands = [f'cd {self.supert_root}']
            if self.environment_name is not None:
                commands.append(f'source {os.environ["CONDA_INIT"]}')
                commands.append(f'conda activate {self.environment_name}')
            commands.append(f'python run_batch.py {input_dir} {output_file}')
            command = ' && '.join(commands)

            logger.info(f'Running command: "{command}"')
            redirect = None if self.verbose else PIPE
            process = Popen(command, stdout=redirect, stderr=redirect, shell=True)
            process.communicate()

            logger.info(f'Loading output from {output_file}')
            output = json.loads(open(output_file, 'r').read())
            metrics_list = []
            for i, summaries in enumerate(summaries_list):
                metrics_list.append([])
                for j in range(len(summaries)):
                    score = output[str(i)][str(j)]
                    # SUPERT will output None if the summary was empty, so we replace that with a 0.0
                    if score is None:
                        score = 0.0
                    metrics_list[-1].append(MetricsDict({'supert': score}))
            return metrics_list


class SUPERTSetupSubcommand(Subcommand):
    @overrides
    def add_subparser(self, parser: argparse._SubParsersAction):
        description = 'Setup the SUPERT metric'
        self.parser = parser.add_parser('supert', description=description, help=description)
        self.parser.set_defaults(subfunc=self.run)

    @overrides
    def run(self, args):
        commands = [
            f'mkdir -p {DATA_ROOT}/metrics',
            f'cd {DATA_ROOT}/metrics',
            f'git clone https://github.com/danieldeutsch/SUPERT',
        ]
        command = ' && '.join(commands)

        process = Popen(command, shell=True)
        process.communicate()

        if process.returncode == 0:
            print('SUPERT setup success')
        else:
            print('SUPERT setup failure')