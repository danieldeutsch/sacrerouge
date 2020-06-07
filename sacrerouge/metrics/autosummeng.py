import argparse
import logging
import os
from collections import defaultdict
from overrides import overrides
from subprocess import Popen, PIPE
from typing import List

from sacrerouge.commands import Subcommand
from sacrerouge.common import DATA_ROOT, TemporaryDirectory
from sacrerouge.common.util import command_exists
from sacrerouge.data import MetricsDict
from sacrerouge.data.fields import ReferencesField, SummaryField
from sacrerouge.data.jackknifers import ReferencesJackknifer
from sacrerouge.data.types import SummaryType
from sacrerouge.metrics import Metric

logger = logging.getLogger(__name__)


@Metric.register('autosummeng')
class AutoSummENG(Metric):
    def __init__(self,
                 min_n: int = 3,
                 max_n: int = 3,
                 d_window: int = 3,
                 min_score: float = 0.0,
                 max_score: float = 1.0,
                 autosummeng_root: str = f'{DATA_ROOT}/metrics/AutoSummENG',
                 verbose: bool = False):
        super().__init__(['references'], jackknifer=ReferencesJackknifer())
        self.min_n = min_n
        self.max_n = max_n
        self.d_window = d_window
        self.min_score = min_score
        self.max_score = max_score
        self.autosummeng_root = autosummeng_root
        self.verbose = verbose

        if not os.path.exists(autosummeng_root):
            raise Exception(f'AutoSummENG path "{autosummeng_root}" does not exist. Have you setup AutoSummENG?')

    def _save_summary(self, summary: SummaryType, file_path: str) -> None:
        dirname = os.path.dirname(file_path)
        if dirname:
            os.makedirs(dirname, exist_ok=True)

        with open(file_path, 'w') as out:
            if isinstance(summary, list):
                out.write('\n'.join(summary))
            else:
                out.write(summary)

    def _parse_output_file(self, file_path: str) -> List[List[MetricsDict]]:
        metrics_dicts = defaultdict(dict)
        with open(file_path, 'r') as f:
            for i, line in enumerate(f):
                # Header
                if i == 0:
                    continue
                columns = line.split('\t')
                if len(columns) != 5:
                    raise Exception(f'Expected 5 columns: {line}')

                instance_index = int(columns[0])
                summarizer_index = int(columns[1])
                metrics_dicts[instance_index][summarizer_index] = MetricsDict({
                    'AutoSummENG': float(columns[2]),
                    'MeMoG': float(columns[3]),
                    'NPowER': float(columns[4])
                })

        metrics_lists = []
        for i in range(len(metrics_dicts)):
            metrics_lists.append([])
            for j in range(len(metrics_dicts[i])):
                metrics_lists[-1].append(metrics_dicts[i][j])
        return metrics_lists

    def _run(self,
             summaries_list: List[List[SummaryType]],
             references_list: List[List[SummaryType]]) -> List[List[MetricsDict]]:
        with TemporaryDirectory() as temp_dir:
            files_tsv_path = f'{temp_dir}/files.tsv'
            with open(files_tsv_path, 'w') as out:
                for i, (summaries, references) in enumerate(zip(summaries_list, references_list)):
                    reference_filenames = []
                    for j, reference in enumerate(references):
                        filename = f'{temp_dir}/references/{i}/{j}.txt'
                        self._save_summary(reference, filename)
                        reference_filenames.append(filename)

                    peer_filenames = []
                    for j, summary in enumerate(summaries):
                        filename = f'{temp_dir}/peers/{i}/{j}.txt'
                        self._save_summary(reference, filename)
                        peer_filenames.append(filename)

                    out.write(f'{",".join(reference_filenames)}\t{",".join(peer_filenames)}\n')

            output_file = f'{temp_dir}/output.tsv'
            args = ' '.join([
                f'-files={files_tsv_path}',
                f'-output={output_file}',
                f'-minN={self.min_n}',
                f'-maxN={self.max_n}',
                f'-dwin={self.d_window}',
                f'-minScore={self.min_score}',
                f'-maxScore={self.max_score}'
            ])

            commands = [
                f'cd {self.autosummeng_root}',
                f'mvn exec:java@NPowERBatch -Dexec.args=\'{args}\''
            ]
            command = ' && '.join(commands)

            logger.info(f'Running AutoSummENG command: "{command}"')
            redirect = None if self.verbose else PIPE
            process = Popen(command, stdout=redirect, stderr=redirect, shell=True)
            stdout, stderr = process.communicate()

            return self._parse_output_file(output_file)

    def score_multi_all(self,
                        summaries_list: List[List[SummaryField]],
                        references_list: List[List[ReferencesField]]) -> List[List[MetricsDict]]:
        # Just take the summaries themselves, not the fields
        summaries_list = [[field.summary for field in fields] for fields in summaries_list]
        references_list = [field.references for field in references_list]

        return self._run(summaries_list, references_list)


class AutoSummENGSetupSubcommand(Subcommand):
    @overrides
    def add_subparser(self, parser: argparse._SubParsersAction):
        self.parser = parser.add_parser('autosummeng')
        self.parser.set_defaults(subfunc=self.run)

    @overrides
    def run(self, args):
        assert command_exists('mvn'), 'AutoSummENG requires Maven to be installed'

        commands = [
            f'mkdir -p {DATA_ROOT}/metrics',
            f'cd {DATA_ROOT}/metrics',
            f'git clone https://github.com/danieldeutsch/AutoSummENG',
            f'cd AutoSummENG',
            f'mvn package'
        ]
        command = ' && '.join(commands)

        process = Popen(command, shell=True)
        process.communicate()

        if process.returncode == 0:
            print('AutoSummENG setup success')
        else:
            print('AutoSummENG setup failure')
