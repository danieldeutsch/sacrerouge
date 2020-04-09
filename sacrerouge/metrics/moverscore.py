import argparse
import numpy as np
from overrides import overrides
from subprocess import Popen, PIPE
from typing import List

from sacrerouge.commands import Subcommand
from sacrerouge.common import DATA_ROOT
from sacrerouge.data import MetricsDict
from sacrerouge.data.fields import ReferencesField, SummaryField
from sacrerouge.data.jackknifers import ReferencesJackknifer
from sacrerouge.data.types import SummaryType
from sacrerouge.metrics import Metric

try:
    from moverscore_v2 import get_idf_dict, word_mover_score

    @Metric.register('moverscore')
    class MoverScore(Metric):
        def __init__(self, moverscore_root: f'{DATA_ROOT}/metrics/MoverScore'):
            super().__init__(['references'], jackknifer=ReferencesJackknifer())
            self.stopwords = set(open(f'{moverscore_root}/stopwords.txt', 'r').read().strip().split())

        def _flatten_summary(self, summary: SummaryType) -> str:
            if isinstance(summary, list):
                return ' '.join(summary)
            return summary

        def _flatten_summaries(self, summaries_list: List[List[SummaryType]]) -> List[List[str]]:
            return [[self._flatten_summary(summary) for summary in summaries] for summaries in summaries_list]

        def _get_unique_summaries(self, summaries_list: List[List[str]]) -> List[str]:
            # Computing MoverScore requires calculating the IDF on the summary and
            # reference set. In sacreROUGE, the scoring functions could potentially
            # repeat references and summaries (e.g., if some of the scoring instances are
            # jackknifing examples), so we should not directly compute IDF on all the
            # summaries, but instead on the unique set of summaries
            unique_summaries = set([summary for summaries in summaries_list for summary in summaries])
            return list(unique_summaries)

        def _run(self,
                 summaries_list: List[List[SummaryType]],
                 references_list: List[List[SummaryType]]) -> List[List[MetricsDict]]:
            summaries_list = self._flatten_summaries(summaries_list)
            references_list = self._flatten_summaries(references_list)

            unique_summaries = self._get_unique_summaries(summaries_list)
            unique_references = self._get_unique_summaries(references_list)

            idf_dict_summaries = get_idf_dict(unique_summaries)
            idf_dict_references = get_idf_dict(unique_references)

            metrics_dict_lists = []
            for summaries, references in zip(summaries_list, references_list):
                metrics_dict_lists.append([])
                for summary in summaries:
                    scores = word_mover_score(references, [summary] * len(references),
                                              idf_dict_references, idf_dict_summaries,
                                              self.stopwords, n_gram=1, remove_subwords=True,
                                              batch_size=48)
                    score = np.mean(scores)
                    metrics_dict_lists[-1].append(MetricsDict({'MoverScore': score}))
            return metrics_dict_lists

        @overrides
        def score_multi_all(self,
                            summaries_list: List[List[SummaryField]],
                            references_list: List[List[ReferencesField]]) -> List[List[MetricsDict]]:
            # Just take the summaries themselves, not the fields
            summaries_list = [[field.summary for field in fields] for fields in summaries_list]
            references_list = [field.references for field in references_list]
            return self._run(summaries_list, references_list)

except ImportError:
    @Metric.register('moverscore')
    class MoverScore(Metric):
        @overrides
        def score_multi_all(self,
                            summaries_list: List[List[SummaryField]],
                            references_list: List[List[ReferencesField]]) -> List[List[MetricsDict]]:
            raise NotImplementedError('Error: "moverscore" python package is not installed')


class MoverScoreSetupSubcommand(Subcommand):
    @overrides
    def add_subparser(self, parser: argparse._SubParsersAction):
        self.parser = parser.add_parser('moverscore')
        self.parser.set_defaults(subfunc=self.run)

    @overrides
    def run(self, args):
        commands = [
            f'mkdir -p {DATA_ROOT}/metrics/MoverScore',
            f'cd {DATA_ROOT}/metrics/MoverScore',
            f'wget https://raw.githubusercontent.com/AIPHES/emnlp19-moverscore/0c9380437706e59ba6510fb755d8836d633a9ea1/examples/stopwords.txt'
        ]
        command = ' && '.join(commands)

        process = Popen(command, shell=True)
        process.communicate()
        if process.returncode == 0:
            print('MoverScore setup success')
        else:
            print('MoverScore setup failure')
