from typing import Any, Dict, List, Tuple, Type

from sacrerouge.common.util import average_metrics
from sacrerouge.data.types import MetricsType, SummaryType


class Metric(object):
    _registry: Dict[str, Type] = {}

    def score(self, summary: SummaryType, *args: List[Any]) -> MetricsType:
        args = [[arg] for arg in args]
        return self.score_all([summary], *args)[0]

    def score_multi(self, summaries: List[SummaryType], *args: List[Any]) -> List[MetricsType]:
        args = [[arg] for arg in args]
        return self.score_multi_all([summaries], *args)[0]

    def score_all(self, summaries: List[SummaryType], *args: List[List[Any]]) -> List[MetricsType]:
        summaries_list = [[summary] for summary in summaries]
        metrics_lists = self.score_multi_all(summaries_list, *args)
        return [metrics_list[0] for metrics_list in metrics_lists]

    def score_multi_all(self, summaries_list: List[List[SummaryType]], *args: List[List[Any]]) -> List[List[MetricsType]]:
        raise NotImplementedError

    def evaluate(self, summaries: List[SummaryType], *args: List[List[Any]]) -> Tuple[MetricsType, List[MetricsType]]:
        micro_metrics_list = self.score_all(summaries, *args)
        macro_metrics = self.aggregate(micro_metrics_list)
        return macro_metrics, micro_metrics_list

    def aggregate(self, metrics_list: List[MetricsType]) -> MetricsType:
        return average_metrics(metrics_list)

    @classmethod
    def register(cls: Type, name: str):
        def _register(subclass: Type):
            cls._registry[name] = subclass
            return subclass
        return _register

    @classmethod
    def from_params(cls: Type, params: Dict[str, Any]) -> 'Metric':
        metric_type = params.pop('type')
        metric_cls = cls._registry[metric_type]
        return metric_cls(**params)
