import argparse
import numpy as np
from collections import defaultdict
from overrides import overrides
from subprocess import Popen
from typing import List

from sacrerouge.commands import Subcommand
from sacrerouge.common import DATA_ROOT
from sacrerouge.data import MetricsDict
from sacrerouge.data.fields import ReferencesField, SummaryField
from sacrerouge.data.jackknifers import ReferencesJackknifer
from sacrerouge.data.types import SummaryType
from sacrerouge.metrics import Metric
from sacrerouge.metrics.metric_subcommand import MetricSubcommand

MOVERSCORE_EXISTS = False

try:
    from moverscore_v2 import get_idf_dict, word_mover_score

    MOVERSCORE_EXISTS = True

    @Metric.register('moverscore')
    class MoverScore(Metric):
        def __init__(self, moverscore_root: str = f'{DATA_ROOT}/metrics/MoverScore'):
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

            # Prepare the inputs into flat lists for faster processing. The
            # indices will keep track of which item the score belongs to
            indices = []
            input_summaries = []
            input_references = []
            for i, (summaries, references) in enumerate(zip(summaries_list, references_list)):
                for j, summary in enumerate(summaries):
                    for reference in references:
                        indices.append((i, j))
                        input_summaries.append(summary)
                        input_references.append(reference)

            # Score all of the data
            scores = word_mover_score(input_references, input_summaries,
                                      idf_dict_references, idf_dict_summaries,
                                      self.stopwords, n_gram=1, remove_subwords=True,
                                      batch_size=48)

            # Compute the mean over the references
            indices_to_scores = defaultdict(list)
            for pair, score in zip(indices, scores):
                indices_to_scores[pair].append(score)

            indices_to_score = {}
            for pair, scores in indices_to_scores.items():
                indices_to_score[pair] = np.mean(scores)

            # Put back into lists
            metrics_dict_lists = []
            for i in range(len(summaries_list)):
                metrics_dict_lists.append([])
                for j in range(len(summaries_list[i])):
                    metrics_dict_lists[-1].append(MetricsDict({
                        'MoverScore': indices_to_score[(i, j)]
                    }))
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


class MoverScoreSetupSubcommand(MetricSubcommand):
    def __init__(self, cr, command_prefix):
        args = []
        super().__init__(cr, command_prefix, "moverscore", args, self.run)

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
