from typing import Any, List, Optional, Tuple

from sacrerouge.common import Registrable
from sacrerouge.data import Jackknifer, MetricsDict
from sacrerouge.data.types import DocumentType, ReferenceType, SummaryType


class Metric(Registrable):
    def __init__(self,
                 required_summary_fields: List[str],
                 required_context_fields: List[str],
                 jackknifer: Optional[Jackknifer] = None) -> None:
        self.required_summary_fields = required_summary_fields
        self.required_context_fields = required_context_fields
        self.jackknifer = jackknifer

    def score(self, *args: List[Any]) -> MetricsDict:
        raise NotImplementedError

    def score_multi(self, *args: List[Any]) -> List[MetricsDict]:
        raise NotImplementedError

    def score_all(self, *args: List[Any]) -> List[MetricsDict]:
        raise NotImplementedError

    def score_multi_all(self, *args: List[Any]) -> List[List[MetricsDict]]:
        raise NotImplementedError

    def evaluate(self, *args: List[Any]) -> Tuple[MetricsDict, List[MetricsDict]]:
        raise NotImplementedError

    def aggregate(self, metrics_list: List[MetricsDict]) -> MetricsDict:
        return sum(metrics_list) / len(metrics_list)

    def requires_jackknifing(self) -> bool:
        return self.jackknifer is not None


class SummaryBasedMetric(Metric):
    """
    A `SummaryBasedMetric` is an evaluation metric that requires just a summary and the context fields. Because
    we know exactly how many summary-specific arguments there will be, we can implement a lot of methods in terms
    of `score_multi_all`, which makes it so a metric developer only has to implement one method.
    """
    def score(self, summary: SummaryType, *args: List[Any]) -> MetricsDict:
        args = [[arg] for arg in args]
        return self.score_all([summary], *args)[0]

    def score_multi(self, summaries: List[SummaryType], *args: List[Any]) -> List[MetricsDict]:
        args = [[arg] for arg in args]
        return self.score_multi_all([summaries], *args)[0]

    def score_all(self, summaries: List[SummaryType], *args: List[List[Any]]) -> List[MetricsDict]:
        summaries_list = [[summary] for summary in summaries]
        metrics_lists = self.score_multi_all(summaries_list, *args)
        return [metrics_list[0] for metrics_list in metrics_lists]

    def score_multi_all(self, summaries_list: List[List[SummaryType]], *args: List[List[Any]]) -> List[List[MetricsDict]]:
        raise NotImplementedError

    def evaluate(self, summaries: List[SummaryType], *args: List[List[Any]]) -> Tuple[MetricsDict, List[MetricsDict]]:
        micro_metrics_list = self.score_all(summaries, *args)
        macro_metrics = self.aggregate(micro_metrics_list)
        return macro_metrics, micro_metrics_list

    def aggregate(self, metrics_list: List[MetricsDict]) -> MetricsDict:
        return sum(metrics_list) / len(metrics_list)

    def requires_jackknifing(self):
        return self.jackknifer is not None


class ReferenceBasedMetric(SummaryBasedMetric):
    """
    This is a dummy class that was created to explicitly define the method arguments. It makes the autocomplete
    in some libraries more helpful by supplying argument names like "references" instead of "*args".
    """
    def score(self, summary: SummaryType, references: List[ReferenceType]) -> MetricsDict:
        return super().score(summary, references)

    def score_multi(self, summaries: List[SummaryType], references: List[ReferenceType]) -> List[MetricsDict]:
        return super().score_multi(summaries, references)

    def score_all(self, summaries: List[SummaryType], references_list: List[List[ReferenceType]]) -> List[MetricsDict]:
        return super().score_all(summaries, references_list)

    def score_multi_all(self, summaries_list: List[List[SummaryType]], references_list: List[List[ReferenceType]]) -> List[List[MetricsDict]]:
        return super().score_multi_all(summaries_list, references_list)

    def evaluate(self, summaries: List[SummaryType], references_list: List[List[ReferenceType]]) -> Tuple[MetricsDict, List[MetricsDict]]:
        return super().evaluate(summaries, references_list)


class DocumentBasedMetric(SummaryBasedMetric):
    """
    This is a dummy class that was created to explicitly define the method arguments. It makes the autocomplete
    in some libraries more helpful by supplying argument names like "documents" instead of "*args".
    """
    def score(self, summary: SummaryType, documents: List[DocumentType]) -> MetricsDict:
        return super().score(summary, documents)

    def score_multi(self, summaries: List[SummaryType], documents: List[DocumentType]) -> List[MetricsDict]:
        return super().score_multi(summaries, documents)

    def score_all(self, summaries: List[SummaryType], documents_list: List[List[DocumentType]]) -> List[MetricsDict]:
        return super().score_all(summaries, documents_list)

    def score_multi_all(self, summaries_list: List[List[SummaryType]], documents_list: List[List[DocumentType]]) -> List[List[MetricsDict]]:
        return super().score_multi_all(summaries_list, documents_list)

    def evaluate(self, summaries: List[SummaryType], documents_list: List[List[DocumentType]]) -> Tuple[MetricsDict, List[MetricsDict]]:
        return super().evaluate(summaries, documents_list)


class ReferenceFreeMetric(SummaryBasedMetric):
    """
    This is a dummy class that was created to explicitly define the method arguments. It makes the autocomplete
    in some libraries more helpful by not supplying the "*args" argument.
    """
    def score(self, summary: SummaryType) -> MetricsDict:
        return super().score(summary)

    def score_multi(self, summaries: List[SummaryType]) -> List[MetricsDict]:
        return super().score_multi(summaries)

    def score_all(self, summaries: List[SummaryType]) -> List[MetricsDict]:
        return super().score_all(summaries)

    def score_multi_all(self, summaries_list: List[List[SummaryType]]) -> List[List[MetricsDict]]:
        return super().score_multi_all(summaries_list)

    def evaluate(self, summaries: List[SummaryType]) -> Tuple[MetricsDict, List[MetricsDict]]:
        return super().evaluate(summaries)
