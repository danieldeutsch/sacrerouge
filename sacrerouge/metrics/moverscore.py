import numpy as np
from overrides import overrides
from typing import List

from sacrerouge.data import MetricsDict
from sacrerouge.data.fields import ReferencesField, SummaryField
from sacrerouge.data.jackknifers import ReferencesJackknifer
from sacrerouge.data.types import SummaryType
from sacrerouge.metrics import Metric

try:
    from moverscore_v2 import get_idf_dict, word_mover_score

    @Metric.register('moverscore')
    class MoverScore(Metric):
        _stopwords = set('i me my myself we our ours ourselves you your yours yourself yourselves he him his himself she her hers herself it its itself they them their theirs themselves what which who whom this that these those am is are was were be been being have has had having do does did doing a an the and but if or because as until while of at by for with about against between into through during before after above below to from up down in out on off over under again further then once here there when where why how all any both each few more most other some such no nor not only own same so than too very s t can will just don should now d ll m o re ve y ain aren couldn didn doesn hadn hasn haven isn ma mightn mustn needn shan shouldn wasn weren won wouldn'.split())

        def __init__(self):
            super().__init__(['references'], jackknifer=ReferencesJackknifer())

        def _flatten_summary(self, summary: SummaryType) -> str:
            if isinstance(summary, list):
                return ' '.join(summary)
            return summary

        def _flatten_summaries(self, summaries_list: List[List[SummaryType]]) -> List[List[str]]:
            return [[self._flatten_summary(summary) for summary in summaries] for summaries in summaries_list]

        def _get_unique_summaries(self, summaries_list: List[List[str]]) -> List[str]:
            # Computing MoverScore requires calculating the IDF on the summary and
            # reference set. In sacreROUGE, the scoring functions could potentially
            # repeat references and summaries (e.g., if some of the scoring instances are
            # jackknifing examples), so we should not directly compute IDF on all the
            # summaries, but instead on the unique set of summaries
            unique_summaries = set([summary for summaries in summaries_list for summary in summaries])
            return list(unique_summaries)

        def _run(self,
                 summaries_list: List[List[SummaryType]],
                 references_list: List[List[SummaryType]]) -> List[List[MetricsDict]]:
            summaries_list = self._flatten_summaries(summaries_list)
            references_list = self._flatten_summaries(references_list)

            unique_summaries = self._get_unique_summaries(summaries_list)
            unique_references = self._get_unique_summaries(references_list)

            idf_dict_summaries = get_idf_dict(unique_summaries)
            idf_dict_references = get_idf_dict(unique_references)

            metrics_dict_lists = []
            for summaries, references in zip(summaries_list, references_list):
                metrics_dict_lists.append([])
                for summary in summaries:
                    scores = word_mover_score(references, [summary] * len(references),
                                              idf_dict_references, idf_dict_summaries,
                                              MoverScore._stopwords, n_gram=1, remove_subwords=True,
                                              batch_size=48)
                    score = np.mean(scores)
                    metrics_dict_lists[-1].append(MetricsDict({'MoverScore': score}))
            return metrics_dict_lists

        @overrides
        def score_multi_all(self,
                            summaries_list: List[List[SummaryField]],
                            references_list: List[List[ReferencesField]]) -> List[List[MetricsDict]]:
            # Just take the summaries themselves, not the fields
            summaries_list = [[field.summary for field in fields] for fields in summaries_list]
            references_list = [field.references for field in references_list]
            return self._run(summaries_list, references_list)

except ImportError:
    @Metric.register('moverscore')
    class MoverScore(Metric):
        @overrides
        def score_multi_all(self,
                            summaries_list: List[List[SummaryField]],
                            references_list: List[List[ReferencesField]]) -> List[List[MetricsDict]]:
            raise NotImplementedError('Error: "moverscore" python package is not installed')
