from overrides import overrides
from typing import List

from sacrerouge.data import MetricsDict
from sacrerouge.data.jackknifers import ReferencesJackknifer
from sacrerouge.data.types import ReferenceType, SummaryType
from sacrerouge.metrics import Metric, ReferenceBasedMetric


@Metric.register('testing')
class TestingMetric(ReferenceBasedMetric):
    def __init__(self) -> None:
        super().__init__(['summary'], ['references'], jackknifer=ReferencesJackknifer())

    @overrides
    def score_multi_all(self,
                        summaries_list: List[List[SummaryType]],
                        references_list: List[List[ReferenceType]]) -> List[List[MetricsDict]]:
        metrics_dict_lists = []
        for summaries, references in zip(summaries_list, references_list):
            metrics_dict_lists.append([])
            for summary in summaries:
                summary_value = float(summary)
                total = 0
                for reference in references:
                    reference_value = float(reference)
                    total += summary_value * reference_value
                metrics_dict_lists[-1].append(MetricsDict({'test': total}))
        return metrics_dict_lists
