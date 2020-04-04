from typing import Any, List, Optional, Tuple

from sacrerouge.common import Registrable
from sacrerouge.data import Jackknifer, MetricsDict
from sacrerouge.data.fields import Field, SummaryField


class Metric(Registrable):
    def __init__(self,
                 required_fields: List[str],
                 jackknifer: Optional[Jackknifer] = None) -> None:
        self.required_fields = required_fields
        self.jackknifer = jackknifer

    def score(self, summary: SummaryField, *args: List[Field]) -> MetricsDict:
        args = [[arg] for arg in args]
        return self.score_all([summary], *args)[0]

    def score_multi(self, summaries: List[SummaryField], *args: List[Field]) -> List[MetricsDict]:
        args = [[arg] for arg in args]
        return self.score_multi_all([summaries], *args)[0]

    def score_all(self, summaries: List[SummaryField], *args: List[List[Field]]) -> List[MetricsDict]:
        summaries_list = [[summary] for summary in summaries]
        metrics_lists = self.score_multi_all(summaries_list, *args)
        return [metrics_list[0] for metrics_list in metrics_lists]

    def score_multi_all(self, summaries_list: List[List[SummaryField]], *args: List[List[Field]]) -> List[List[MetricsDict]]:
        raise NotImplementedError

    def evaluate(self, summaries: List[SummaryField], *args: List[List[Any]]) -> Tuple[MetricsDict, List[MetricsDict]]:
        micro_metrics_list = self.score_all(summaries, *args)
        macro_metrics = self.aggregate(micro_metrics_list)
        return macro_metrics, micro_metrics_list

    def aggregate(self, metrics_list: List[MetricsDict]) -> MetricsDict:
        return sum(metrics_list) / len(metrics_list)

    def requires_jackknifing(self):
        return self.jackknifer is not None
