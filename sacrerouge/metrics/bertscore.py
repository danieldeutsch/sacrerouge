import argparse
import os
from bert_score import score
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


@Metric.register('bertscore')
class BertScore(Metric):
    def __init__(self,
                 model_type: str = None,
                 num_layers: int = None,
                 nthreads: int = 4,
                 batch_size: int = 64,
                 lang: str = 'en',
                 verbose: bool = False) -> None:
        super().__init__(['references'], jackknifer=ReferencesJackknifer())
        self.model_type = model_type
        self.num_layers = num_layers
        self.nthreads = nthreads
        self.batch_size = batch_size
        self.lang = lang
        self.verbose = verbose

    def _flatten_summary(self, summary: SummaryType) -> str:
        if isinstance(summary, list):
            return ' '.join(summary)
        return summary

    def _run(self,
             summaries_list: List[List[SummaryType]],
             references_list: List[List[SummaryType]]) -> List[List[MetricsDict]]:
        summaries_list = [[self._flatten_summary(summary) for summary in summaries] for summaries in summaries_list]
        references_list = [[self._flatten_summary(reference) for reference in references] for references in references_list]

        # Create the candidate and reference lists for passing to the scoring function
        input_candidates = []
        input_references = []
        for summaries, references in zip(summaries_list, references_list):
            for summary in summaries:
                input_candidates.append(summary)
                input_references.append(references)

        # Score the summaries
        precisions, recalls, fs1s = score(input_candidates, input_references,
                                          model_type=self.model_type,
                                          num_layers=self.num_layers,
                                          nthreads=self.nthreads,
                                          batch_size=self.batch_size,
                                          lang=self.lang,
                                          verbose=self.verbose)

        # Remap the scores to the summaries
        index = 0
        metrics_lists = []
        for summaries in summaries_list:
            metrics_lists.append([])
            for summary in summaries:
                metrics_lists[-1].append(MetricsDict({
                    'bertscore': {
                        'precision': precisions[index].item(),
                        'recall': recalls[index].item(),
                        'f1': fs1s[index].item(),
                    }
                }))
                index += 1

        return metrics_lists

    def score_multi_all(self,
                        summaries_list: List[List[SummaryField]],
                        references_list: List[List[ReferencesField]]) -> List[List[MetricsDict]]:
        # Just take the summaries themselves, not the fields
        summaries_list = [[field.summary for field in fields] for fields in summaries_list]
        references_list = [field.references for field in references_list]

        return self._run(summaries_list, references_list)
