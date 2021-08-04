from repro.models import Model
from typing import List

from sacrerouge.data import MetricsDict
from sacrerouge.data.types import ReferenceType, SummaryType
from sacrerouge.metrics import ReferenceBasedMetric


class ReferenceBasedDockerMetric(ReferenceBasedMetric):
    def __init__(self, metric: Model):
        super().__init__()
        self.metric = metric

    def score_multi_all(self,
                        summaries_list: List[List[SummaryType]],
                        references_list: List[List[ReferenceType]]) -> List[List[MetricsDict]]:
        # The repro version of the metric does not support grouping in its interface, so we
        # have to ungroup, then regroup at the end
        inputs = []
        for summaries, references in zip(summaries_list, references_list):
            for summary in summaries:
                inputs.append({
                    "candidate": summary,
                    "references": references
                })

        _, scores = self.metric.predict_batch(inputs)

        grouped_scores = []
        index = 0
        for summaries in summaries_list:
            grouped_scores.append([])
            for _ in summaries:
                grouped_scores[-1].append(MetricsDict(scores[index]))
                index += 1
        return grouped_scores
