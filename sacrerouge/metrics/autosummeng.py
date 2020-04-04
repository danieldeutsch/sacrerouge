import argparse
from overrides import overrides
from subprocess import Popen, PIPE
from typing import List

from sacrerouge.commands import Subcommand
from sacrerouge.common import DATA_ROOT, TemporaryDirectory
from sacrerouge.data import MetricsDict
from sacrerouge.data.fields import ReferencesField, SummaryField
from sacrerouge.data.jackknifers import ReferencesJackknifer
from sacrerouge.data.types import SummaryType
from sacrerouge.metrics import Metric


@Metric.register('autosummeng')
class AutoSummENG(Metric):
    def __init__(self,
                 min_n: int = 3,
                 max_n: int = 3,
                 d_window: int = 3,
                 min_score: float = 0.0,
                 max_score: float = 1.0,
                 autosummeng_root: str = f'{DATA_ROOT}/metrics/AutoSummENG'):
        super().__init__(['references'], jackknifer=ReferencesJackknifer())
        self.min_n = min_n
        self.max_n = max_n
        self.d_window = d_window
        self.min_score = min_score
        self.max_score = max_score
        self.autosummeng_root = autosummeng_root

    def _save_summary(self, summary: SummaryType, file_path: str) -> None:
        with open(file_path, 'w') as out:
            if isinstance(summary, list):
                out.write('\n'.join(summary))
            else:
                out.write(summary)

    def _run(self,
             summary: SummaryType,
             references: List[SummaryType]) -> MetricsDict:
        with TemporaryDirectory() as temp_dir:
            summary_file_path = f'{temp_dir}/peer.txt'
            self._save_summary(summary, summary_file_path)

            reference_file_paths = []
            for i, reference in enumerate(references):
                reference_file_path = f'{temp_dir}/model.{i}.txt'
                reference_file_paths.append(reference_file_path)
                self._save_summary(reference, reference_file_path)

            commands = [
                f'cd {self.autosummeng_root}/Releases/V1',
                ' '.join([
                    f'java',
                    f'-cp NPowER.jar:lib/JInsect.jar:lib/OpenJGraph.jar',
                    f'gr.demokritos.iit.npower.NPowER',
                    f'-peer={summary_file_path}',
                    f'-models={":".join(reference_file_paths)}',
                    f'-allScores',
                    f'-minN={self.min_n}',
                    f'-maxN={self.max_n}',
                    f'-dwin={self.d_window}',
                    f'-minScore={self.min_score}',
                    f'-maxScore={self.max_score}'
                ])
            ]
            process = Popen(' && '.join(commands), stdout=PIPE, stderr=PIPE, shell=True)
            stdout, stderr = process.communicate()

            columns = stdout.decode().strip().split()
            if len(columns) != 3:
                raise Exception(f'Expected 3 columns. Found {len(columns)}')

            autosummeng, memog, npower = list(map(float, columns))
            return MetricsDict({
                'AutoSummENG': autosummeng,
                'MeMoG': memog,
                'NPowER': npower
            })

    def score_multi_all(self,
                        summaries_list: List[List[SummaryField]],
                        references_list: List[List[ReferencesField]]) -> List[List[MetricsDict]]:
        # Just take the summaries themselves, not the fields
        summaries_list = [[field.summary for field in fields] for fields in summaries_list]
        references_list = [field.references for field in references_list]

        metrics_lists = []
        for summaries, references in zip(summaries_list, references_list):
            metrics_list = []
            for summary in summaries:
                metrics_list.append(self._run(summary, references))
            metrics_lists.append(metrics_list)
        return metrics_lists


class AutoSummENGSetupSubcommand(Subcommand):
    @overrides
    def add_subparser(self, parser: argparse._SubParsersAction):
        self.parser = parser.add_parser('autosummeng')
        self.parser.set_defaults(subfunc=self.run)

    @overrides
    def run(self, args):
        commands = [
            f'mkdir -p {DATA_ROOT}/metrics',
            f'cd {DATA_ROOT}/metrics',
            f'git clone https://github.com/ggianna/SummaryEvaluation AutoSummENG'
        ]
        command = ' && '.join(commands)

        process = Popen(command, shell=True)
        process.communicate()

        if process.returncode == 0:
            print('AutoSummENG setup success')
        else:
            print('AutoSummENG setup failure')
