import logging
import numpy as np
import warnings
from typing import Callable, List, Optional, Tuple, Union

from sacrerouge.data import Metrics

ArrayLike = Union[List, np.ndarray]
Corr = Optional[float]
CorrFunc = Callable[[ArrayLike, ArrayLike], Tuple[float, float]]
PValue = Optional[float]

logger = logging.getLogger(__name__)


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


def summary_level_corr(corr_func: CorrFunc,
                       X: np.ndarray,
                       Y: np.ndarray,
                       return_num_instances: bool = False,
                       return_individual_correlations: bool = False,
                       return_correlations_num_inputs: bool = False,
                       silent: bool = False) -> Corr:
    """
    Calculates the summary-level correlation between the matrices X and Y. If `return_num_instances` is True,
    the number of non-NaN individual correlations is returned. If `return_individual_correlations` is True,
    the individual correlations will be returned. If `return_correlations_num_inputs is True, the number of
    non-NaN inputs for each individual correlation will be returned. If `silent` is True, no warning message
    will be logged if there is a NaN correlation.
    """
    # The entries must be the same shape and any nan in one must correspond to a nan in the other
    assert X.shape == Y.shape
    np.testing.assert_array_equal(np.isnan(X), np.isnan(Y))

    M = X.shape[1]
    correlations = []
    num_inputs = []
    num_nan = 0
    for j in range(M):
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore')

            # Pick the column that corresponds to input j
            x, y = X[:, j], Y[:, j]
            # Remove any possible nans. Because X and Y have nans in the same positions,
            # this will still leave comparable parallel data
            x = x[~np.isnan(x)]
            y = y[~np.isnan(y)]
            r, _ = corr_func(x, y)
            if np.isnan(r):
                num_nan += 1
            else:
                correlations.append(r)
                num_inputs.append(len(x))

    if not silent and num_nan > 0:
        logger.warning(f'Skipped {num_nan} summary-level correlations because they were NaN')

    if len(correlations) > 0:
        r = sum(correlations) / len(correlations)
        num_instances = len(correlations)
    else:
        r, num_instances = None, 0

    output = (r,)
    if return_num_instances:
        output = output + (num_instances,)
    if return_individual_correlations:
        output = output + (correlations,)
    if return_correlations_num_inputs:
        output = output + (num_inputs,)

    if len(output) == 1:
        return output[0]
    return output


def system_level_corr(corr_func: CorrFunc,
                      X: np.ndarray,
                      Y: np.ndarray,
                      return_pvalue: bool = False) -> Union[Corr, Tuple[Corr, PValue]]:
    """
    Calculates the system-level correlation between X and Y, where the system-level score is equal to the
    average over the inputs, ignoring NaNs.
    """
    # The entries must be the same shape and any nan in one must correspond to a nan in the other
    assert X.shape == Y.shape
    np.testing.assert_array_equal(np.isnan(X), np.isnan(Y))
    with warnings.catch_warnings():
        warnings.filterwarnings('ignore')

        # Take the system score by averaging over inputs, ignoring nans
        x = np.nanmean(X, axis=1)
        y = np.nanmean(Y, axis=1)

        r, pvalue = corr_func(x, y)
        if np.isnan(r):
            r, pvalue = None, None
        if return_pvalue:
            return r, pvalue
        return r


def global_corr(corr_func: CorrFunc, X: np.ndarray, Y: np.ndarray,
                return_pvalue: bool = False) -> Union[Corr, Tuple[Corr, PValue]]:
    """
    Calculates the global correlation between X and Y, which is simply the correlation of
    all of the values in the matrices.
    """
    # The entries must be the same shape and any nan in one must correspond to a nan in the other
    assert X.shape == Y.shape
    np.testing.assert_array_equal(np.isnan(X), np.isnan(Y))
    with warnings.catch_warnings():
        warnings.filterwarnings('ignore')

        x, y = X.flatten(), Y.flatten()
        # Remove any possible nans. Because X and Y have nans in the same positions,
        # this will still leave comparable parallel data
        x = x[~np.isnan(x)]
        y = y[~np.isnan(y)]

        r, pvalue = corr_func(x, y)
        if np.isnan(r):
            r, pvalue = None, None
        if return_pvalue:
            return r, pvalue
        return r
