from typing import Any, Dict, List, Tuple, Type

from sacrerouge.data.types import MetricsType, SummaryType


class Metric(object):
    _registry: Dict[str, Type] = {}

    def _accumulate(self, cumulative: MetricsType, other: MetricsType):
        for key, value in other.items():
            if isinstance(value, dict):
                if key not in cumulative:
                    cumulative[key] = {}
                self._accumulate(cumulative[key], other[key])
            else:
                if key not in cumulative:
                    cumulative[key] = value
                else:
                    cumulative[key] += value

    def _divide(self, results: MetricsType, number: float):
        divided = {}
        for key, value in results.items():
            if isinstance(value, dict):
                divided[key] = self._divide(results[key], number)
            else:
                divided[key] = value / number
        return divided

    def score_all(self,
                  summaries: List[SummaryType],
                  references_list: List[List[SummaryType]]) -> Tuple[MetricsType, List[MetricsType]]:
        cumulative_results = {}
        individual_results = []

        for summary, references in zip(summaries, references_list):
            results = self.score(summary, references)
            self._accumulate(cumulative_results, results)
            individual_results.append(results)

        aggregated_results = self._divide(cumulative_results, len(individual_results))
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
