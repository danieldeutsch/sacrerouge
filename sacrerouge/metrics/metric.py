from typing import Any, Dict, List, Tuple, Type

from sacrerouge.common.util import average_metrics
from sacrerouge.data.types import MetricsType, SummaryType


class Metric(object):
    _registry: Dict[str, Type] = {}

    def score_all(self,
                  summaries: List[SummaryType],
                  references_list: List[List[SummaryType]]) -> Tuple[MetricsType, List[MetricsType]]:
        individual_results = []
        for summary, references in zip(summaries, references_list):
            results = self.score(summary, references)
            individual_results.append(results)

        aggregated_results = average_metrics(individual_results)
        return aggregated_results, individual_results

    def score(self,
              summary: SummaryType,
              references: List[SummaryType]) -> MetricsType:
        raise NotImplementedError

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
