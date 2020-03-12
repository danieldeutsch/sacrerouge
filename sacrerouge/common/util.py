import collections
from typing import List

from sacrerouge.data.types import MetricsType


# https://gist.github.com/angstwad/bf22d1822c38a92ec0a9
def merge_dict(dct, merge_dct):
    """ Recursive dict merge. Inspired by :meth:``dict.update()``, instead of
    updating only top-level keys, dict_merge recurses down into dicts nested
    to an arbitrary depth, updating keys. The ``merge_dct`` is merged into
    ``dct``.
    :param dct: dict onto which the merge is executed
    :param merge_dct: dct merged into dct
    :return: None
    """
    for k, v in merge_dct.items():
        if (k in dct and isinstance(dct[k], dict) and isinstance(merge_dct[k], collections.Mapping)):
            merge_dict(dct[k], merge_dct[k])
        else:
            dct[k] = merge_dct[k]


def sum_metrics(metrics_list: List[MetricsType]) -> MetricsType:
    def _accumulate_metrics(target: MetricsType, source: MetricsType) -> None:
        for key, value in source.items():
            if isinstance(value, dict):
                if key not in target:
                    target[key] = {}
                _accumulate_metrics(target[key], source[key])
            else:
                if key not in target:
                    target[key] = value
                else:
                    target[key] += value

    total = {}
    for metrics in metrics_list:
        _accumulate_metrics(total, metrics)
    return total


def divide_metrics(metrics: MetricsType, denominator: float) -> MetricsType:
    divided = {}
    for key, value in metrics.items():
        if isinstance(value, dict):
            divided[key] = divide_metrics(metrics[key], denominator)
        else:
            divided[key] = value / denominator
    return divided


def average_metrics(metrics_list: List[MetricsType]) -> MetricsType:
    total = sum_metrics(metrics_list)
    return divide_metrics(total, len(metrics_list))
