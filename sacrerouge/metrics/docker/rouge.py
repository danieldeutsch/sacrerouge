from typing import List
from repro.models.lin2004 import ROUGE

from sacrerouge.data import MetricsDict
from sacrerouge.data.types import ReferenceType
from sacrerouge.data.types import SummaryType
from sacrerouge.metrics import Metric, ReferenceBasedMetric


@Metric.register('docker-rouge')
class DockerRouge(ReferenceBasedMetric):
    def __init__(
        self,
        image: str = "lin2004",
        ngram_order: int = 4,
        porter_stemmer: bool = True,
        remove_stopwords: bool = False,
        sentence_split: bool = True,
        calculate_su4: bool = True,
    ):
        super().__init__()
        self.metric = ROUGE(
            image=image,
            ngram_order=ngram_order,
            porter_stemmer=porter_stemmer,
            remove_stopwords=remove_stopwords,
            sentence_split=sentence_split,
            calculate_su4=calculate_su4,
        )

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
