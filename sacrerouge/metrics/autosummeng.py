from subprocess import Popen, PIPE
from typing import List

from sacrerouge.common import TemporaryDirectory
from sacrerouge.data.types import MetricsType, SummaryType
from sacrerouge.metrics import Metric


@Metric.register('autosummeng')
class AutoSummENG(Metric):
    def __init__(self,
                 min_n: int = 3,
                 max_n: int = 3,
                 d_window: int = 3,
                 min_score: float = 0.0,
                 max_score: float = 1.0,
                 npower_root: str = 'external/AutoSummENG/SummaryEvaluation/Releases/V1'):
        super().__init__()
        self.min_n = min_n
        self.max_n = max_n
        self.d_window = d_window
        self.min_score = min_score
        self.max_score = max_score
        self.npower_root = npower_root

    def _save_summary(self, summary: SummaryType, file_path: str) -> None:
        with open(file_path, 'w') as out:
            if isinstance(summary, list):
                out.write('\n'.join(summary))
            else:
                out.write(summary)

    def score(self,
              summary: SummaryType,
              references: List[SummaryType]) -> MetricsType:
        with TemporaryDirectory() as temp_dir:
            summary_file_path = f'{temp_dir}/peer.txt'
            self._save_summary(summary, summary_file_path)

            reference_file_paths = []
            for i, reference in enumerate(references):
                reference_file_path = f'{temp_dir}/model.{i}.txt'
                reference_file_paths.append(reference_file_path)
                self._save_summary(reference, reference_file_path)

            commands = [
                f'cd {self.npower_root}',
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
            return {
                'AutoSummENG': autosummeng,
                'MeMoG': memog,
                'NPowER': npower
            }
