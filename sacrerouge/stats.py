import numpy as np
from collections import defaultdict
from typing import List, Union

from sacrerouge.data import Metrics


def convert_to_matrices(metrics_list: List[Metrics], *metric_names: str) -> Union[np.ndarray, List[np.ndarray]]:
    """
    Creates an N x M matrix of scores for each metric in `metric_names`, where N is the number of summarizer_ids
    and M is the number of instance_ids. Entry (i, j) in the matrix will be metric's score for the i-th summarizer
    and j-th input document. If no score exists, the entry in the matrix will be np.nan. One matrix will be returned
    for each name in `metric_names`.
    """
    summarizer_ids = set()
    instance_ids = set()
    scores = {name: {} for name in metric_names}
    for metrics in metrics_list:
        instance_ids.add(metrics.instance_id)
        summarizer_ids.add(metrics.summarizer_id)
        for name in metric_names:
            if name in metrics.metrics:
                scores[name][(metrics.instance_id, metrics.summarizer_id)] = metrics.metrics[name]

    instance_ids = sorted(instance_ids)
    summarizer_ids = sorted(summarizer_ids)
    N = len(summarizer_ids)
    M = len(instance_ids)
    matrices = [np.ndarray((N, M)) for _ in metric_names]
    for i, summarizer_id in enumerate(summarizer_ids):
        for j, instance_id in enumerate(instance_ids):
            for k, name in enumerate(metric_names):
                try:
                    matrices[k][i, j] = scores[name][(instance_id, summarizer_id)]
                except KeyError:
                    matrices[k][i, j] = np.nan

    if len(matrices) == 1:
        return matrices[0]
    return matrices