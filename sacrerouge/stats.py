import logging
import numpy as np
import scipy.stats
import warnings
from scipy.stats import kendalltau, pearsonr, spearmanr
from typing import Callable, Dict, List, Optional, Tuple, Union

from sacrerouge.data import Metrics

ArrayLike = Union[List, np.ndarray]
Corr = Optional[float]
CorrFunc = Callable[[ArrayLike, ArrayLike], Tuple[float, float]]
PValue = Optional[float]
SummaryCorrFunc = Callable[[ArrayLike, ArrayLike], Union[float, Tuple[float, float]]]

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


def bootstrap_system_sample(*matrices: np.ndarray) -> Union[np.ndarray, List[np.ndarray]]:
    """
    Resamples new matrices by sampling systems with replacement. The sample will be taken in parallel for all of
    the input matrices.
    """
    N, M = matrices[0].shape
    for matrix in matrices:
        assert matrix.shape == (N, M)
    rows = np.random.choice(N, N, replace=True)
    samples = [matrix[rows] for matrix in matrices]
    if len(samples) == 1:
        return samples[0]
    return samples


def bootstrap_input_sample(*matrices: np.ndarray) -> Union[np.ndarray, List[np.ndarray]]:
    """
    Resamples new matrices by sampling inputs with replacement. The sample will be taken in parallel for all of
    the input matrices.
    """
    N, M = matrices[0].shape
    for matrix in matrices:
        assert matrix.shape == (N, M)
    cols = np.random.choice(M, M, replace=True)
    samples = [matrix[:, cols] for matrix in matrices]
    if len(samples) == 1:
        return samples[0]
    return samples


def bootstrap_both_sample(*matrices: np.ndarray) -> Union[np.ndarray, List[np.ndarray]]:
    """
    Resamples new matrices by sampling both systems and inputs with replacement. The sample will be the intersection of
    the sampled systems and inputs. The sample will be taken in parallel for all of the input matrices.
    """
    N, M = matrices[0].shape
    for matrix in matrices:
        assert matrix.shape == (N, M)
    rows = np.random.choice(N, N, replace=True)
    cols = np.random.choice(M, M, replace=True)
    samples = [matrix[rows][:, cols] for matrix in matrices]
    if len(samples) == 1:
        return samples[0]
    return samples


def bootstrap_ci(corr_func: SummaryCorrFunc,
                 X: np.ndarray,
                 Y: np.ndarray,
                 sample_func: Callable,
                 alpha: float = 0.05,
                 num_samples: int = 1000) -> Tuple[float, float]:
    """
    Calculates a bootstrap-based confidence interval using the correlation function and X and Y. The `corr_func` should
    be the system-, summary- or global level correlations with a Pearson, Spearman, or Kendall function passed as its
    first argument. `sample_func` is the bootstrapping sample function that should be used to take the subsamples.
    The lower and upper bounds for the (1-alpha)*100% confidence interval will be returned (i.e., alpha / 2 in each tail).
    """
    assert X.shape == Y.shape
    samples = []
    for _ in range(num_samples):
        x, y = sample_func(X, Y)
        r = corr_func(x, y)
        if r is not None:
            # Value is ignored if it is NaN
            samples.append(r)
    lower = np.percentile(samples, alpha / 2 * 100)
    upper = np.percentile(samples, (1.0 - alpha / 2) * 100)
    return lower, upper


def _get_n(corr_func: SummaryCorrFunc, X: np.ndarray) -> int:
    """
    Calculates the number of observations that would be used to calculate the correlation.
    """
    if corr_func.func == summary_level_corr:
        # Assume n is the summary-correlation with the largest n. We find that by counting how many non-nans
        # are in each column, then taking the max
        return (~np.isnan(X)).sum(axis=0).max()
    elif corr_func.func == system_level_corr:
        # Count the number of systems with at least 1 score. We can probably safely just take X.shape[0], but
        # this is extra careful
        return ((~np.isnan(X)).sum(axis=1) > 0).sum()
    elif corr_func.func == global_corr:
        # The number of non-nan elements
        return (~np.isnan(X)).sum()
    else:
        raise Exception(f'Unknown summary correlation function {corr_func.func}')


def fisher_ci(corr_func: SummaryCorrFunc,
              X: np.ndarray,
              Y: np.ndarray,
              alpha: float = 0.05,
              **kwargs) -> Tuple[Optional[float], Optional[float]]:
    """
    Calculates a confidence interval via the Fisher transformation. See Bonett and Wright (200) for details.
    """
    # The Fisher transformation has constants that depend on the correlation coefficient being used. Inspecting
    # the correlation function is kind of hacky, but it works.
    assert len(corr_func.args) == 1
    assert corr_func.args[0] in [pearsonr, spearmanr, kendalltau]

    r = corr_func(X, Y)
    if corr_func.args[0] == pearsonr:
        b, c = 3, 1
    elif corr_func.args[0] == spearmanr:
        b, c = 3, np.sqrt(1 + r ** 2 / 2)
    elif corr_func.args[0] == kendalltau:
        b, c = 4, np.sqrt(.437)
    else:
        raise Exception(f'Unexpected correlation function: {corr_func.args[0]}')

    n = _get_n(corr_func, X)
    if n > b:
        z_r = np.arctanh(r)
        z = scipy.stats.norm.ppf(1.0 - alpha / 2)
        z_l = z_r - z * c / np.sqrt(n - b)
        z_u = z_r + z * c / np.sqrt(n - b)
        r_l = np.tanh(z_l)
        r_u = np.tanh(z_u)
    else:
        r_l, r_u = None, None
    return r_l, r_u


def corr_ci(corr_func: SummaryCorrFunc,
            X: np.ndarray,
            Y: np.ndarray,
            method: Optional[str],
            alpha: float = 0.05,
            two_tailed: bool = True,
            kwargs: Dict = None) -> Tuple[Optional[float], Optional[float]]:
    """
    Calculates a (1-alpha) * 100% confidence interval. The kwargs argument will be passed as **kwargs to the
    confidence interval method
    """
    kwargs = kwargs or {}

    # If we are doing a single-tailed test, we need to double the alpha value because the CI methods will
    # always be run for two-tailed with alpha / 2 in each tail.
    if not two_tailed:
        alpha = alpha * 2

    if method is None or method == 'none':
        return None, None
    elif method == 'bootstrap-system':
        return bootstrap_ci(corr_func, X, Y, bootstrap_system_sample, alpha=alpha, **kwargs)
    elif method == 'bootstrap-input':
        return bootstrap_ci(corr_func, X, Y, bootstrap_input_sample, alpha=alpha, **kwargs)
    elif method == 'bootstrap-both':
        return bootstrap_ci(corr_func, X, Y, bootstrap_both_sample, alpha=alpha, **kwargs)
    elif method == 'fisher':
        return fisher_ci(corr_func, X, Y, alpha=alpha, **kwargs)
    else:
        raise Exception(f'Unknown confidence interval method: {method}')


def random_bool_mask(*dims: int) -> np.ndarray:
    return np.random.rand(*dims) > 0.5


def permute_systems(X: np.ndarray, Y: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """
    Samples new matrices by randomly permuting the systems between X and Y. The original matrices
    will not be changed.
    """
    assert X.shape == Y.shape
    # Do not modify the original matrices
    X_p = X.copy()
    Y_p = Y.copy()

    mask = random_bool_mask(X.shape[0], 1).reshape((X.shape[0],))
    X_p[mask] = Y[mask]
    Y_p[mask] = X[mask]
    return X_p, Y_p


def permute_inputs(X: np.ndarray, Y: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """
    Samples new matrices by randomly permuting the inputs between X and Y. The original matrices
    will not be changed.
    """
    assert X.shape == Y.shape
    # Do not modify the original matrices
    X_p = X.copy()
    Y_p = Y.copy()

    mask = random_bool_mask(1, X.shape[1]).reshape((X.shape[1],))
    X_p[:, mask] = Y[:, mask]
    Y_p[:, mask] = X[:, mask]
    return X_p, Y_p


def permute_both(X: np.ndarray, Y: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """
    Samples new matrices by randomly permuting the systems and inputs between X and Y. The original matrices
    will not be changed.
    """
    assert X.shape == Y.shape
    # Do not modify the original matrices
    X_p = X.copy()
    Y_p = Y.copy()

    mask = random_bool_mask(X.shape[0], X.shape[1])
    np.putmask(X_p, mask, Y)
    np.putmask(Y_p, mask, X)
    return X_p, Y_p


def bootstrap_diff_test(corr_func: SummaryCorrFunc,
                        X: np.ndarray,
                        Y: np.ndarray,
                        Z: np.ndarray,
                        sample_func: Callable,
                        two_tailed: bool,
                        num_samples: int = 1000,
                        return_test_statistic: bool = False,
                        return_deltas: bool = False) -> float:
    """
    Calculates a p-value using a paired bootstrap test. If `return_test_statistic` is True, the original delta
    is returned. If `return_deltas` is True, all of the non-NaN bootstrap sample deltas are returned. A one-tailed
    test will calculate a p-value for corr(X, Z) > corr(Y, Z)
    """
    delta_orig = corr_func(X, Z) - corr_func(Y, Z)
    if two_tailed:
        # If the test is two tailed, then we count how often we see any difference between delta and delta_orig
        # with an absolute value larger than 2 * delta_org. We do this by always taking the absolute value of each
        # of the deltas
        delta_orig = abs(delta_orig)

    deltas = []
    count = 0
    successful_trials = 0
    for _ in range(num_samples):
        X_i, Y_i, Z_i = sample_func(X, Y, Z)
        try:
            delta = corr_func(X_i, Z_i) - corr_func(Y_i, Z_i)
            if two_tailed:
                delta = abs(delta)

            # The pseudocode for this in "An Empirical Investigation of Statistical Significance in NLP" in
            # Berg-Kirkpatrick et al. (2012) shows delta > 2 * delta_orig. I think the only time it really matters
            # if it's > or >= is if the two score matrices are identical. If they are the same, delta_orig is 0
            # and every delta would be 0. Using > would mean the count never gets incremented, resulting in a p-value
            # of 0, which is not correct. Using >= would mean the count gets incremented every time, resulting in a
            # p-value of 1, which is correct.
            if delta >= 2 * delta_orig:
                count += 1
            successful_trials += 1
            deltas.append(delta)
        except TypeError:
            pass
    pvalue = count / successful_trials

    output = (pvalue,)
    if return_test_statistic:
        output = output + (delta_orig,)
    if return_deltas:
        output = output + (deltas,)

    if len(output) == 1:
        return output[0]
    return output


def standardize(X: np.ndarray) -> np.ndarray:
    return (X - np.nanmean(X)) / np.nanstd(X)


def permutation_diff_test(corr_func: SummaryCorrFunc,
                          X: np.ndarray,
                          Y: np.ndarray,
                          Z: np.ndarray,
                          permute_func: Callable,
                          two_tailed: bool,
                          num_permutations: int = 1000,
                          return_test_statistic: bool = False,
                          return_deltas: bool = False) -> float:
    """
    Calculates a p-value based on a permutation test. If `return_test_statistic` is True, the original detal will
    be returned. If `return_deltas` is True, all of the resampled deltas will be returned. A one-tailed test will
    calculate a p-value for corr(X, Z) > corr(Y, Z)
    """
    # The data needs to be standardized so the metrics are on the same scale. It doesn't matter
    # if we standardize Z because Pearson will first standardize it, Spearman/Kendall will rank it
    # (standardization invariant)
    X = standardize(X)
    Y = standardize(Y)
    delta_orig = corr_func(X, Z) - corr_func(Y, Z)
    if two_tailed:
        # If the test is two tailed, then we count how often we see any difference between delta and delta_orig
        # with an absolute value larger than 2 * delta_org. We do this by always taking the absolute value of each
        # of the deltas
        delta_orig = abs(delta_orig)

    deltas = []
    count = 0
    for _ in range(num_permutations):
        X_p, Y_p = permute_func(X, Y)
        delta = corr_func(X_p, Z) - corr_func(Y_p, Z)
        if two_tailed:
            delta = abs(delta)

        # See note about >= versus > in bootstrap_diff_test
        if delta >= delta_orig:
            count += 1
        deltas.append(delta)
    pvalue = (count + 1) / (num_permutations + 1)  # +1 for the original delta

    output = (pvalue,)
    if return_test_statistic:
        output = output + (delta_orig,)
    if return_deltas:
        output = output + (deltas,)

    if len(output) == 1:
        return output[0]
    return output


def williams_diff_test(corr_func: SummaryCorrFunc,
                       X: np.ndarray,
                       Y: np.ndarray,
                       Z: np.ndarray,
                       two_tailed: bool) -> float:
    """
    Calculates the p-value for the difference in correlations using Williams' Test.
    """
    # In the math, Z is metric 1. We take the absolute value of the correlations because
    # it does not matter whether they are positively or negatively correlated with each other. The WMT scripts
    # do the same before calling r.test
    r12 = abs(corr_func(X, Z))
    r13 = abs(corr_func(Y, Z))
    r23 = abs(corr_func(X, Y))
    n = _get_n(corr_func, X)

    # Implementation based on https://github.com/cran/psych/blob/master/R/r.test.R
    diff = r12 - r13
    det = 1 - (r12 ** 2) - (r23 ** 2) - (r13 ** 2) + (2 * r12 * r23 * r13)
    av = (r12 + r13) / 2
    cube = (1 - r23) ** 3
    t2 = diff * np.sqrt((n - 1) * (1 + r23) / (((2 * (n - 1) / (n - 3)) * det + av ** 2 * cube)))

    # r.test implicitly assumes that r12 > r13 because it takes the absolute value of the t statistic. Since we don't,
    # we have to have special handling for one-tailed tests so we don't map a negative t statistic to a positive one.
    if two_tailed:
        pvalue = scipy.stats.t.sf(abs(t2), n - 3) * 2
    else:
        pvalue = scipy.stats.t.sf(t2, n - 3)
    return pvalue


def corr_diff_test(corr_func: SummaryCorrFunc,
                   X: np.ndarray,
                   Y: np.ndarray,
                   Z: np.ndarray,
                   method: str,
                   two_tailed: bool,
                   kwargs: Dict = None) -> Optional[float]:
    """
    Runs a hypothesis test to calculate a p-value for the difference between corr(X, Z) and corr(Y, Z). If `two_tailed`
    is False, H0 is corr(X, Z) <= corr(Y, Z) and H1 is corr(X, Z) > corr(Y, Z). The kwargs argument will be passed
    as **kwargs to the hypothesis test method.
    """
    kwargs = kwargs or {}

    if method is None or method == 'none':
        return None
    elif method == 'bootstrap-system':
        return bootstrap_diff_test(corr_func, X, Y, Z, bootstrap_system_sample, two_tailed, **kwargs)
    elif method == 'bootstrap-input':
        return bootstrap_diff_test(corr_func, X, Y, Z, bootstrap_input_sample, two_tailed, **kwargs)
    elif method == 'bootstrap-both':
        return bootstrap_diff_test(corr_func, X, Y, Z, bootstrap_both_sample, two_tailed, **kwargs)
    elif method == 'permutation-both':
        return permutation_diff_test(corr_func, X, Y, Z, permute_both, two_tailed, **kwargs)
    elif method == 'permutation-system':
        return permutation_diff_test(corr_func, X, Y, Z, permute_systems, two_tailed, **kwargs)
    elif method == 'permutation-input':
        return permutation_diff_test(corr_func, X, Y, Z, permute_inputs, two_tailed, **kwargs)
    elif method == 'williams':
        return williams_diff_test(corr_func, X, Y, Z, two_tailed)
    else:
        raise Exception(f'Unknown hypothesis test method: {method}')


def bonferroni_partial_conjunction_pvalue_test(pvalues: List[float], alpha: float = 0.05) -> Tuple[int, List[int]]:
    N = len(pvalues)

    pvalues_with_indices = [(p, i) for i, p in enumerate(pvalues)]
    pvalues_with_indices = sorted(pvalues_with_indices)
    pvalues = [p for p, _ in pvalues_with_indices]
    indices = [i for _, i in pvalues_with_indices]

    p_u = [(N - (u + 1) + 1) * pvalues[u] for u in range(N)]  # (u + 1) because this is 0-indexed
    p_star = []
    k_hat = 0
    for u in range(N):
        if u == 0:
            p_star.append(p_u[u])
        else:
            p_star.append(max(p_star[-1], p_u[u]))
        if p_star[-1] <= alpha:
            k_hat += 1

    # The Holm procedure will always reject the lowest p-values
    significant_datasets = indices[:k_hat]
    return k_hat, significant_datasets


def partial_conjunction_pvalue_test(method: str, pvalues: List[float], alpha: float = 0.05) -> Tuple[int, List[int]]:
    if method == 'bonferroni':
        return bonferroni_partial_conjunction_pvalue_test(pvalues, alpha=alpha)
    raise Exception(f'Unknown partial conjunction p-value test: {method}')
