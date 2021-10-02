from repro.models.deutsch2021 import DEFAULT_IMAGE, QAEval
from typing import List, T

from sacrerouge.data import MetricsDict
from sacrerouge.data.types import ReferenceType
from sacrerouge.data.types import SummaryType
from sacrerouge.metrics import Metric, ReferenceBasedMetric


@Metric.register('docker-qa-eval')
class DockerQAEval(ReferenceBasedMetric):
    def __init__(self,
                 image: str = DEFAULT_IMAGE,
                 device: int = 0,
                 generation_batch_size: int = 8,
                 answering_batch_size: int = 8,
                 lerc_batch_size: int = 8) -> None:
        super().__init__()
        self.metric = QAEval(
            image=image,
            device=device,
            generation_batch_size=generation_batch_size,
            answering_batch_size=answering_batch_size,
            lerc_batch_size=lerc_batch_size,
        )

    @staticmethod
    def _regroup_results(results: List[T], summaries_list: List[List[SummaryType]]) -> List[List[T]]:
        grouped_results = []
        index = 0
        for summaries in summaries_list:
            grouped_results.append([])
            for _ in summaries:
                grouped_results[-1].append(results[index])
                index += 1
        return grouped_results

    def score_multi_all(self,
                        summaries_list: List[List[SummaryType]],
                        references_list: List[List[ReferenceType]],
                        return_qa_pairs: bool = False) -> List[List[MetricsDict]]:
        # The repro version of the metric does not support grouping in its interface, so we
        # have to ungroup, then regroup at the end
        inputs = []
        for summaries, references in zip(summaries_list, references_list):
            for summary in summaries:
                inputs.append({
                    "candidate": summary,
                    "references": references
                })

        outputs = self.metric.predict_batch(inputs, return_qa_pairs=return_qa_pairs)
        scores_list = [MetricsDict(output) for output in outputs[1]]

        if return_qa_pairs:
            qa_pairs_list = outputs[2]
            combined = [(scores, qa_pairs) for scores, qa_pairs in zip(scores_list, qa_pairs_list)]
            grouped_output = self._regroup_results(combined, summaries_list)
            return grouped_output
        else:
            grouped_scores = self._regroup_results(scores_list, summaries_list)
            return grouped_scores
