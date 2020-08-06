import argparse
import logging
import os
from collections import defaultdict
from overrides import overrides
from subprocess import Popen, PIPE
from typing import List, Dict, Tuple

from sacrerouge.commands import Subcommand
from sacrerouge.common import DATA_ROOT, TemporaryDirectory
from sacrerouge.data import MetricsDict
from sacrerouge.data.jackknifers import ReferencesJackknifer
from sacrerouge.data.types import ReferenceType, SummaryType
from sacrerouge.metrics import Metric, ReferenceBasedMetric

logger = logging.getLogger(__name__)


@Metric.register('meteor')
class Meteor(ReferenceBasedMetric):
    def __init__(self, meteor_root: str = f'{DATA_ROOT}/metrics/METEOR'):
        super().__init__(['summary'], ['references'], jackknifer=ReferencesJackknifer())
        self.meteor_root = meteor_root
        if not os.path.exists(meteor_root):
            raise Exception(f'Path "{meteor_root}" does not exist. Have you setup METEOR?')

    def _flatten_summaries(self, summaries_list: List[List[SummaryType]]) -> List[List[str]]:
        flattened_list = []
        for summaries in summaries_list:
            flattened_list.append([])
            for summary in summaries:
                if isinstance(summary, list):
                    summary = ' '.join(summary)
                flattened_list[-1].append(summary)
        return flattened_list

    def _parse_meteor_stdout(self, stdout: str) -> Tuple[float, List[float]]:
        lines = stdout.splitlines()
        assert lines[11].startswith('Segment 1 score'), 'Unexpected Meteor stdout format'

        individual_scores = []
        for line in lines[11:]:
            if not line.startswith('Segment'):
                break
            columns = line.split()
            individual_scores.append(float(columns[3]))

        assert lines[-1].startswith('Final score:'), 'Unexpected Meteor stdout format'
        columns = lines[-1].split()
        final_score = float(columns[2])

        return final_score, individual_scores

    def _aggregate_summary_scores(self,
                                  summaries_list: List[List[str]],
                                  references_list: List[List[str]],
                                  tuple_to_indices: Dict[Tuple[int, int], List[int]],
                                  individual_scores: List[float]) -> List[List[MetricsDict]]:
        metrics_lists = []
        for i, (summaries, references) in enumerate(zip(summaries_list, references_list)):
            metrics_lists.append([])
            for j, summary in enumerate(summaries):
                scores = [individual_scores[index] for index in tuple_to_indices[(i, j)]]
                metrics_lists[-1].append(MetricsDict({
                    'METEOR': sum(scores) / len(scores)
                }))
        return metrics_lists

    def _run(self,
             summaries_list: List[List[SummaryType]],
             references_list: List[List[SummaryType]]) -> Tuple[MetricsDict, List[List[MetricsDict]]]:
        summaries_list = self._flatten_summaries(summaries_list)
        references_list = self._flatten_summaries(references_list)

        with TemporaryDirectory() as temp_dir:
            # As far as I can tell, the input only allows for one reference
            # per input, so we need to write an instance for every pair and then
            # aggregate the output
            summaries_file = f'{temp_dir}/summaries.txt'
            references_file = f'{temp_dir}/references.txt'
            index = 0
            tuple_to_indices = defaultdict(list)
            with open(summaries_file, 'w') as out_summaries:
                with open(references_file, 'w') as out_references:
                    for i, (summaries, references) in enumerate(zip(summaries_list, references_list)):
                        for j, summary in enumerate(summaries):
                            for reference in references:
                                out_summaries.write(summary + '\n')
                                out_references.write(reference + '\n')
                                tuple_to_indices[(i, j)].append(index)
                                index += 1

            # Run meteor
            command = [
                'java', '-jar', f'{self.meteor_root}/meteor-1.5/meteor-1.5.jar',
                summaries_file, references_file,
                '-l', 'en',
                '-norm'
            ]

            logger.info(f'Running METEOR command: "{command}"')
            process = Popen(command, stdout=PIPE, stderr=PIPE)
            stdout, stderr = process.communicate()
            if stderr:
                raise Exception(f'Meteor failed with stderr: {stderr.decode()}')

            final_score, individual_scores = self._parse_meteor_stdout(stdout.decode())

            macro_metrics = MetricsDict({'METEOR': final_score})
            micro_metrics_list = self._aggregate_summary_scores(summaries_list, references_list, tuple_to_indices, individual_scores)
            return macro_metrics, micro_metrics_list

    def score_multi_all(self,
                        summaries_list: List[List[SummaryType]],
                        references_list: List[List[ReferenceType]]) -> List[List[MetricsDict]]:
        _, micro_metrics_lists = self._run(summaries_list, references_list)
        return micro_metrics_lists

    def evaluate(self,
                 summaries: List[SummaryType],
                 references_list: List[List[ReferenceType]]) -> Tuple[MetricsDict, List[MetricsDict]]:
        summaries_list = [[summary] for summary in summaries]
        macro_metrics, micro_metrics_lists = self._run(summaries_list, references_list)
        micro_metrics_list = [metrics_list[0] for metrics_list in micro_metrics_lists]
        return macro_metrics, micro_metrics_list


class MeteorSetupSubcommand(Subcommand):
    @overrides
    def add_subparser(self, parser: argparse._SubParsersAction):
        description = 'Setup the METEOR metric'
        self.parser = parser.add_parser('meteor', description=description, help=description)
        self.parser.set_defaults(subfunc=self.run)

    @overrides
    def run(self, args):
        commands = [
            f'mkdir -p {DATA_ROOT}/metrics/METEOR',
            f'cd {DATA_ROOT}/metrics/METEOR',
            f'wget https://www.cs.cmu.edu/~alavie/METEOR/download/meteor-1.5.tar.gz',
            f'tar xzvf meteor-1.5.tar.gz'
        ]
        command = ' && '.join(commands)

        process = Popen(command, shell=True)
        process.communicate()
        if process.returncode == 0:
            print('METEOR setup success')
        else:
            print('METEOR setup failure')
