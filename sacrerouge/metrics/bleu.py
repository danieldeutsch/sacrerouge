import logging
from sacrebleu import BLEU
from typing import List

from sacrerouge.common.util import flatten
from sacrerouge.data import MetricsDict
from sacrerouge.data.types import ReferenceType
from sacrerouge.data.types import SummaryType
from sacrerouge.metrics import Metric, ReferenceBasedMetric

logger = logging.getLogger(__name__)


@Metric.register('sent-bleu')
class SentBleu(ReferenceBasedMetric):
    def __init__(self, **kwargs) -> None:
        """
        Args:
            **kwargs: The kwargs that will be passed to `sacrebleu.BLEU`. See
                the `sacrebleu` documentation for details.
        """
        super().__init__()
        if "effective_order" not in kwargs:
            kwargs["effective_order"] = True
        self.bleu = BLEU(**kwargs)

    def score_multi_all(
        self,
        summaries_list: List[List[SummaryType]],
        references_list: List[List[ReferenceType]],
        **kwargs,
    ) -> List[List[MetricsDict]]:
        scores_list = []
        for summaries, references in zip(summaries_list, references_list):
            references = [flatten(reference) for reference in references]
            scores_list.append([])
            for summary in summaries:
                summary = flatten(summary)
                score = self.bleu.sentence_score(summary, references)
                scores_list[-1].append(MetricsDict({'sent-bleu': score.score}))
        return scores_list
