import math
from collections import Counter
from typing import List, Tuple

from sacrerouge.data import MetricsDict, Pyramid, PyramidAnnotation
from sacrerouge.data.jackknifers import PyramidJackknifer
from sacrerouge.metrics import Metric


@Metric.register('pyramid-score')
class PyramidScore(Metric):
    """
    Implements calculating the modified pyramid score based on the description from page 7
    of https://www.cis.upenn.edu/~nenkova/papers/p1-nenkova.pdf and section 3 of
    http://www.cs.columbia.edu/nlp/papers/2005/passonneau_al_05.pdf.
    """
    def __init__(self, name_override: str = None):
        super().__init__(['annotation'], ['pyramid'], PyramidJackknifer())
        self.name = name_override or 'modified_pyramid_score'

    def score(self, annotation: PyramidAnnotation, pyramid: Pyramid) -> MetricsDict:
        # Create a mapping from the SCU id to its weight and count how many are at each weight
        scu_id_to_weight = {}
        weight_to_num_scus = Counter()
        for scu in pyramid.scus:
            weight = scu.get_weight()
            scu_id_to_weight[scu.scu_id] = weight
            weight_to_num_scus[weight] += 1

        # Calculate the total weight of the SCUs in the annotation
        total_weight = 0
        for scu in annotation.scus:
            # It's possible the SCU id isn't in the Pyramid, for example, if we are
            # doing jackknifing and the reference corresponding to an SCU of weight 1 was removed
            if scu.scu_id in scu_id_to_weight:
                total_weight += scu_id_to_weight[scu.scu_id]

        # Calculate the average number of SCUs in the pyramid summaries
        total_scus = 0
        for i in range(len(pyramid.summarizer_ids)):
            total_scus += len(pyramid.get_scu_id_set(i))
        average_num_scus = total_scus / len(pyramid.summarizer_ids)

        # Calculate the weight of an ideal summary with `average_num_scus` SCUs
        ideal_weight = 0
        scus_remaining = int(math.ceil(average_num_scus))
        for weight in sorted(weight_to_num_scus.keys(), reverse=True):
            if scus_remaining <= 0:
                break
            possible_scus = weight_to_num_scus[weight]
            num_scus_taken = min(scus_remaining, possible_scus)
            ideal_weight += num_scus_taken * weight
            scus_remaining -= num_scus_taken

        # The modified pyramid score is the ratio of the weight to the ideal weight
        return MetricsDict({self.name: total_weight / ideal_weight})

    def score_multi(self, annotations: List[PyramidAnnotation], pyramid: Pyramid) -> List[MetricsDict]:
        return self.score_multi_all([annotations], [pyramid])[0]

    def score_all(self, annotations: List[PyramidAnnotation], pyramids: List[Pyramid]) -> List[MetricsDict]:
        annotation_list = [[annotation] for annotation in annotations]
        metrics_lists = self.score_multi_all(annotation_list, pyramids)
        return [metrics_list[0] for metrics_list in metrics_lists]

    def score_multi_all(self, annotations_list: List[List[PyramidAnnotation]], pyramids: List[Pyramid]) -> List[List[MetricsDict]]:
        metrics_dict_lists = []
        for annotations, pyramid in zip(annotations_list, pyramids):
            metrics_dict_lists.append([])
            for annotation in annotations:
                metrics_dict_lists[-1].append(self.score(annotation, pyramid))
        return metrics_dict_lists

    def evaluate(self, annotations: List[PyramidAnnotation], pyramids: List[Pyramid]) -> Tuple[MetricsDict, List[MetricsDict]]:
        micro_metrics_list = self.score_all(annotations, pyramids)
        macro_metrics = self.aggregate(micro_metrics_list)
        return macro_metrics, micro_metrics_list
