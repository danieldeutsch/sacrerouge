import functools
import numpy as np
import unittest
from scipy.stats import kendalltau, pearsonr, spearmanr

from sacrerouge.data import Metrics
from sacrerouge.stats import convert_to_matrices, summary_level_corr, system_level_corr, global_corr, \
    bootstrap_system_sample, bootstrap_input_sample, bootstrap_both_sample, bootstrap_ci, fisher_ci, corr_ci, \
    random_bool_mask, permute_systems, permute_inputs, permute_both, bootstrap_diff_test, permutation_diff_test, \
    williams_diff_test


class TestStats(unittest.TestCase):
    def test_convert_to_matrices(self):
        metrics_list = [
            Metrics('1', 'A', 'peer', {'m1': 1, 'm2': 2, 'm3': 3}),
            Metrics('2', 'A', 'peer', {'m1': 4, 'm2': 5}),
            Metrics('1', 'B', 'peer', {'m1': 6, 'm2': 7, 'm3': 8}),
            Metrics('2', 'B', 'peer', {'m1': 9, 'm2': 10, 'm3': 11}),
        ]
        m1 = convert_to_matrices(metrics_list, 'm1')
        np.testing.assert_array_equal(m1, [[1, 4], [6, 9]])

        m1, m2 = convert_to_matrices(metrics_list, 'm1', 'm2')
        np.testing.assert_array_equal(m1, [[1, 4], [6, 9]])
        np.testing.assert_array_equal(m2, [[2, 5], [7, 10]])

        m3 = convert_to_matrices(metrics_list, 'm3')
        np.testing.assert_array_equal(m3, [[3, np.nan], [8, 11]])

        metrics_list = [
            Metrics('1', 'A', 'peer', {'m1': 1, 'm2': 2}),
            Metrics('2', 'A', 'peer', {'m1': 4, 'm2': 5}),
            Metrics('1', 'B', 'peer', {'m1': 6, 'm2': 7}),
            Metrics('3', 'B', 'peer', {'m1': 2, 'm2': 9}),
        ]
        m1 = convert_to_matrices(metrics_list, 'm1')
        np.testing.assert_array_equal(m1, [[1, 4, np.nan], [6, np.nan, 2]])

    def test_summary_level_corr(self):
        # This will end up skipping the last column because the scores are identical,
        # so the correlation is NaN
        X = np.array([
            [1, 9, 2],
            [4, 5, 2],
            [6, 7, 2]
        ])
        Y = np.array([
            [11, 12, 13],
            [14, 15, 16],
            [17, 18, 19]
        ])
        r = summary_level_corr(pearsonr, X, Y)
        self.assertAlmostEqual(r, 0.2466996339, places=4)

        X = np.array([
            [1, 2],
            [1, 2],
        ])
        Y = np.array([
            [11, 12],
            [14, 15],
        ])
        # This shouldn't have any correlations because both are NaN
        assert summary_level_corr(pearsonr, X, Y) is None

        X = np.array([
            [1, 9, 2],
            [np.nan, 5, 4],
            [6, 7, 7]
        ])
        Y = np.array([
            [11, 12, 13],
            [np.nan, 15, 16],
            [17, 18, 19]
        ])
        self.assertAlmostEqual(summary_level_corr(pearsonr, X, Y), 0.4977997559)

        # Fails because they do not have parallel nans
        X = np.array([
            [1, 9, 2],
            [4, np.nan, 2],
            [6, 7, 2]
        ])
        Y = np.array([
            [11, 12, np.nan],
            [14, 15, 16],
            [17, 18, 19]
        ])
        with self.assertRaises(Exception):
            summary_level_corr(pearsonr, X, Y)

    def test_system_level_corr(self):
        X = np.array([
            [1, 9, 2],
            [4, 5, 2],
            [6, 7, 2]
        ])
        Y = np.array([
            [11, 12, 13],
            [14, 15, 16],
            [17, 18, 19]
        ])
        r = system_level_corr(pearsonr, X, Y)
        self.assertAlmostEqual(r, 0.7205766921, places=4)

        r, pvalue = system_level_corr(pearsonr, X, Y, return_pvalue=True)
        self.assertAlmostEqual(r, 0.7205766921, places=4)
        self.assertAlmostEqual(pvalue, 0.48775429164459994, places=4)

        X = np.array([
            [1, 9, 2],
            [4, 5, np.nan],
            [6, np.nan, 2]
        ])
        Y = np.array([
            [11, 12, 13],
            [14, 15, np.nan],
            [17, np.nan, 19]
        ])
        r = system_level_corr(pearsonr, X, Y)
        self.assertAlmostEqual(r, -0.09578262852, places=4)

        r, pvalue = system_level_corr(pearsonr, X, Y, return_pvalue=True)
        self.assertAlmostEqual(r, -0.09578262852, places=4)
        self.assertAlmostEqual(pvalue, 0.938929260614949, places=4)

        X = np.array([
            [1, 2],
            [1, 2],
        ])
        Y = np.array([
            [11, 12],
            [14, 15],
        ])
        # This shouldn't have any correlations because the average of X is all the same
        assert system_level_corr(pearsonr, X, Y) is None
        assert system_level_corr(pearsonr, X, Y, return_pvalue=True) == (None, None)

        # Fails because they do not have parallel nans
        X = np.array([
            [1, 9, 2],
            [4, np.nan, 2],
            [6, 7, 2]
        ])
        Y = np.array([
            [11, 12, np.nan],
            [14, 15, 16],
            [17, 18, 19]
        ])
        with self.assertRaises(Exception):
            system_level_corr(pearsonr, X, Y)

    def test_global_corr(self):
        X = np.array([
            [1, 9, 2],
            [4, 5, 2],
            [6, 7, 2]
        ])
        Y = np.array([
            [11, 12, 13],
            [14, 15, 16],
            [17, 18, 19]
        ])
        r = global_corr(pearsonr, X, Y)
        self.assertAlmostEqual(r, 0.06691496051, places=4)

        r, pvalue = global_corr(pearsonr, X, Y, return_pvalue=True)
        self.assertAlmostEqual(r, 0.06691496051, places=4)
        self.assertAlmostEqual(pvalue, 0.8641895868792804, places=4)

        X = np.array([
            [1, 9, 2],
            [np.nan, 5, 2],
            [6, 7, np.nan]
        ])
        Y = np.array([
            [11, 12, 13],
            [np.nan, 15, 16],
            [17, 18, np.nan]
        ])
        r = global_corr(pearsonr, X, Y)
        self.assertAlmostEqual(r, 0.2897249422, places=4)

        r, pvalue = global_corr(pearsonr, X, Y, return_pvalue=True)
        self.assertAlmostEqual(r, 0.2897249422, places=4)
        self.assertAlmostEqual(pvalue, 0.5285282548518477, places=4)

        X = np.array([
            [1, 1],
            [1, 1],
        ])
        Y = np.array([
            [11, 12],
            [14, 15],
        ])
        # This shouldn't have any correlations because X is identical
        assert global_corr(pearsonr, X, Y) is None
        assert global_corr(pearsonr, X, Y, return_pvalue=True) == (None, None)

        # Fails because they do not have parallel nans
        X = np.array([
            [1, 9, 2],
            [4, np.nan, 2],
            [6, 7, 2]
        ])
        Y = np.array([
            [11, 12, np.nan],
            [14, 15, 16],
            [17, 18, 19]
        ])
        with self.assertRaises(Exception):
            global_corr(pearsonr, X, Y)

    def test_bootstrap_system_sample(self):
        A = np.array([
            [1, 2, 3, 4],
            [5, 6, 7, 8],
            [9, 10, 11, 12]
        ])
        B = np.array([
            [13, 14, 15, 16],
            [17, 18, 19, 20],
            [21, 22, 23, 24]
        ])

        # We check what sample should be taken with this random seed
        np.random.seed(4)
        np.testing.assert_array_equal(np.random.choice(3, 3, replace=True), [2, 2, 1])

        np.random.seed(4)
        A_s = bootstrap_system_sample(A)
        np.testing.assert_array_equal(A_s, [[9, 10, 11, 12], [9, 10, 11, 12], [5, 6, 7, 8]])

        np.random.seed(4)
        A_s, B_s = bootstrap_system_sample(A, B)
        np.testing.assert_array_equal(A_s, [[9, 10, 11, 12], [9, 10, 11, 12], [5, 6, 7, 8]])
        np.testing.assert_array_equal(B_s, [[21, 22, 23, 24], [21, 22, 23, 24], [17, 18, 19, 20]])

    def test_bootstrap_input_sample(self):
        A = np.array([
            [1, 2, 3, 4],
            [5, 6, 7, 8],
            [9, 10, 11, 12]
        ])
        B = np.array([
            [13, 14, 15, 16],
            [17, 18, 19, 20],
            [21, 22, 23, 24]
        ])

        # We check what sample should be taken with this random seed
        np.random.seed(4)
        np.testing.assert_array_equal(np.random.choice(4, 4, replace=True), [2, 2, 3, 1])

        np.random.seed(4)
        A_s = bootstrap_input_sample(A)
        np.testing.assert_array_equal(A_s, [[3, 3, 4, 2], [7, 7, 8, 6], [11, 11, 12, 10]])

        np.random.seed(4)
        A_s, B_s = bootstrap_input_sample(A, B)
        np.testing.assert_array_equal(A_s, [[3, 3, 4, 2], [7, 7, 8, 6], [11, 11, 12, 10]])
        np.testing.assert_array_equal(B_s, [[15, 15, 16, 14], [19, 19, 20, 18], [23, 23, 24, 22]])

    def test_bootstrap_both_sample(self):
        A = np.array([
            [1, 2, 3, 4],
            [5, 6, 7, 8],
            [9, 10, 11, 12]
        ])
        B = np.array([
            [13, 14, 15, 16],
            [17, 18, 19, 20],
            [21, 22, 23, 24]
        ])

        # We check what sample should be taken with this random seed
        np.random.seed(4)
        np.testing.assert_array_equal(np.random.choice(3, 3, replace=True), [2, 2, 1])
        np.testing.assert_array_equal(np.random.choice(4, 4, replace=True), [1, 0, 3, 0])

        np.random.seed(4)
        A_s = bootstrap_both_sample(A)
        np.testing.assert_array_equal(A_s, [[10, 9, 12, 9], [10, 9, 12, 9], [6, 5, 8, 5]])

        np.random.seed(4)
        A_s, B_s = bootstrap_both_sample(A, B)
        np.testing.assert_array_equal(A_s, [[10, 9, 12, 9], [10, 9, 12, 9], [6, 5, 8, 5]])
        np.testing.assert_array_equal(B_s, [[22, 21, 24, 21], [22, 21, 24, 21], [18, 17, 20, 17]])

    def test_bootstrap_ci(self):
        # Regression test
        np.random.seed(3)
        X = np.array([
            [1, 2, 3],
            [4, 5, 6],
            [7, 8, 9]
        ])
        Y = np.array([
            [5, 2, 7],
            [1, 7, 3],
            [4, 2, 2]
        ])
        corr_func = functools.partial(global_corr, pearsonr)

        lower, upper = bootstrap_ci(corr_func, X, Y, bootstrap_system_sample)
        self.assertAlmostEqual(lower, -0.8660254037844388, places=4)
        self.assertAlmostEqual(upper, 0.39735970711951324, places=4)

        lower, upper = bootstrap_ci(corr_func, X, Y, bootstrap_system_sample, alpha=0.1)
        self.assertAlmostEqual(lower, -0.5773502691896258, places=4)
        self.assertAlmostEqual(upper, 0.32732683535398865, places=4)

        lower, upper = bootstrap_ci(corr_func, X, Y, bootstrap_input_sample)
        self.assertAlmostEqual(lower, -0.9449111825230679, places=4)
        self.assertAlmostEqual(upper, 0.0, places=4)

        lower, upper = bootstrap_ci(corr_func, X, Y, bootstrap_both_sample)
        self.assertAlmostEqual(lower, -1.0, places=4)
        self.assertAlmostEqual(upper, 1.0, places=4)

    def test_fisher_ci(self):
        pearson_global = functools.partial(global_corr, pearsonr)
        spearman_global = functools.partial(global_corr, spearmanr)
        kendall_global = functools.partial(global_corr, kendalltau)

        pearson_system = functools.partial(system_level_corr, pearsonr)
        spearman_system = functools.partial(system_level_corr, spearmanr)
        kendall_system = functools.partial(system_level_corr, kendalltau)

        pearson_summary = functools.partial(summary_level_corr, pearsonr)
        spearman_summary = functools.partial(summary_level_corr, spearmanr)
        kendall_summary = functools.partial(summary_level_corr, kendalltau)

        np.random.seed(12)
        X = np.random.rand(5, 7)
        Y = np.random.rand(5, 7)

        self.assertAlmostEqual(fisher_ci(pearson_global, X, Y), (-0.02763744135012373, 0.5818846438651135), places=4)
        self.assertAlmostEqual(fisher_ci(spearman_global, X, Y), (-0.06733469087453943, 0.5640758668009686), places=4)
        self.assertAlmostEqual(fisher_ci(kendall_global, X, Y), (-0.029964677270600665, 0.4098565164085108), places=4)

        self.assertAlmostEqual(fisher_ci(pearson_system, X, Y), (-0.6445648014599665, 0.9644395142168088), places=4)
        self.assertAlmostEqual(fisher_ci(spearman_system, X, Y), (-0.6708734441360908, 0.9756771001362685), places=4)
        self.assertAlmostEqual(fisher_ci(kendall_system, X, Y), (-0.7023910748254728, 0.9377789575997956), places=4)

        self.assertAlmostEqual(fisher_ci(pearson_summary, X, Y), (-0.808376631595968, 0.9287863878043723), places=4)
        self.assertAlmostEqual(fisher_ci(spearman_summary, X, Y), (-0.7262127280589684, 0.9653646507719408), places=4)
        self.assertAlmostEqual(fisher_ci(kendall_summary, X, Y), (-0.684486849088761, 0.9418063314024349), places=4)

    def test_corr_ci(self):
        # Regression test
        np.random.seed(3)
        X = np.array([
            [1, 2, 3],
            [4, 5, 6],
            [7, 8, 9]
        ])
        Y = np.array([
            [5, 2, 7],
            [1, 7, 3],
            [4, 2, 2]
        ])
        corr_func = functools.partial(global_corr, pearsonr)

        # Make sure we get the same result going through bootstrap_ci and corr_ci
        expected_lower, expected_upper = bootstrap_ci(corr_func, X, Y, bootstrap_system_sample)
        lower, upper = corr_ci(corr_func, X, Y, 'bootstrap-system')
        self.assertAlmostEqual(lower, expected_lower, places=4)
        self.assertAlmostEqual(upper, expected_upper, places=4)

        expected_lower, expected_upper = bootstrap_ci(corr_func, X, Y, bootstrap_input_sample)
        lower, upper = corr_ci(corr_func, X, Y, 'bootstrap-input')
        self.assertAlmostEqual(lower, expected_lower, places=4)
        self.assertAlmostEqual(upper, expected_upper, places=4)

        expected_lower, expected_upper = bootstrap_ci(corr_func, X, Y, bootstrap_both_sample)
        lower, upper = corr_ci(corr_func, X, Y, 'bootstrap-both')
        self.assertAlmostEqual(lower, expected_lower, places=4)
        self.assertAlmostEqual(upper, expected_upper, places=4)

        # If we do a single tail, the result should be the same with alpha / 2
        expected_lower, expected_upper = bootstrap_ci(corr_func, X, Y, bootstrap_system_sample)
        lower, upper = corr_ci(corr_func, X, Y, 'bootstrap-system', alpha=0.025, two_tailed=False)
        self.assertAlmostEqual(lower, expected_lower, places=4)
        self.assertAlmostEqual(upper, expected_upper, places=4)

        # None cases
        assert corr_ci(corr_func, X, Y, None) == (None, None)
        assert corr_ci(corr_func, X, Y, 'none') == (None, None)

        with self.assertRaises(Exception):
            corr_ci(corr_func, X, Y, 'does-not-exist')

    def test_random_bool_mask(self):
        np.random.seed(7)
        expected_rand = [
            [0.07630829, 0.77991879, 0.43840923, 0.72346518],
            [0.97798951, 0.53849587, 0.50112046, 0.07205113],
            [0.26843898, 0.4998825,  0.67923,    0.80373904]
        ]
        np.testing.assert_array_almost_equal(np.random.rand(3, 4), expected_rand)

        np.random.seed(7)
        expected_mask = [
            [False, True, False, True],
            [True, True, True, False],
            [False, False, True, True]
        ]
        mask = random_bool_mask(3, 4)
        np.testing.assert_array_equal(mask, expected_mask)

    def test_permute_systems(self):
        X = np.arange(1, 13).reshape(3, 4)
        Y = -np.arange(1, 13).reshape(3, 4)

        np.random.seed(7)
        expected_mask = [[False], [True], [False]]
        mask = random_bool_mask(3, 1)
        np.testing.assert_array_equal(mask, expected_mask)

        np.random.seed(7)
        expected_X = [
            [1, 2, 3, 4],
            [-5, -6, -7, -8],
            [9, 10, 11, 12]
        ]
        expected_Y = [
            [-1, -2, -3, -4],
            [5, 6, 7, 8],
            [-9, -10, -11, -12]
        ]
        X_p, Y_p = permute_systems(X, Y)
        np.testing.assert_array_equal(X_p, expected_X)
        np.testing.assert_array_equal(Y_p, expected_Y)
        np.testing.assert_array_equal(X, np.arange(1, 13).reshape(3, 4))
        np.testing.assert_array_equal(Y, -np.arange(1, 13).reshape(3, 4))

    def test_permute_inputs(self):
        X = np.arange(1, 13).reshape(3, 4)
        Y = -np.arange(1, 13).reshape(3, 4)

        np.random.seed(7)
        expected_mask = [[False, True, False, True]]
        mask = random_bool_mask(1, 4)
        np.testing.assert_array_equal(mask, expected_mask)

        np.random.seed(7)
        expected_X = [
            [1, -2, 3, -4],
            [5, -6, 7, -8],
            [9, -10, 11, -12]
        ]
        expected_Y = [
            [-1, 2, -3, 4],
            [-5, 6, -7, 8],
            [-9, 10, -11, 12]
        ]
        X_p, Y_p = permute_inputs(X, Y)
        np.testing.assert_array_equal(X_p, expected_X)
        np.testing.assert_array_equal(Y_p, expected_Y)
        np.testing.assert_array_equal(X, np.arange(1, 13).reshape(3, 4))
        np.testing.assert_array_equal(Y, -np.arange(1, 13).reshape(3, 4))

    def test_permute_both(self):
        X = np.arange(1, 13).reshape(3, 4)
        Y = -np.arange(1, 13).reshape(3, 4)

        np.random.seed(7)
        expected_mask = [
            [False, True, False, True],
            [True, True, True, False],
            [False, False, True, True]
        ]
        mask = random_bool_mask(3, 4)
        np.testing.assert_array_equal(mask, expected_mask)

        # The True values should swap and the original matrices should be unchanged
        np.random.seed(7)
        expected_X = [
            [1, -2, 3, -4],
            [-5, -6, -7, 8],
            [9, 10, -11, -12]
        ]
        expected_Y = [
            [-1, 2, -3, 4],
            [5, 6, 7, -8],
            [-9, -10, 11, 12]
        ]
        X_p, Y_p = permute_both(X, Y)
        np.testing.assert_array_equal(X_p, expected_X)
        np.testing.assert_array_equal(Y_p, expected_Y)
        np.testing.assert_array_equal(X, np.arange(1, 13).reshape(3, 4))
        np.testing.assert_array_equal(Y, -np.arange(1, 13).reshape(3, 4))

    def test_bootstrap_diff_test(self):
        # Regression test
        np.random.seed(12)
        X = np.random.random((9, 5))
        Y = np.random.random((9, 5))
        Z = np.random.random((9, 5))
        corr_func = functools.partial(global_corr, pearsonr)

        np.random.seed(2)
        assert bootstrap_diff_test(corr_func, X, Y, Z, bootstrap_system_sample, False) == 0.958
        np.random.seed(2)
        assert bootstrap_diff_test(corr_func, Y, X, Z, bootstrap_system_sample, False) == 0.042

    def test_permutation_diff_test(self):
        # Regression test
        np.random.seed(12)
        X = np.random.random((9, 5))
        Y = np.random.random((9, 5))
        Z = np.random.random((9, 5))
        corr_func = functools.partial(global_corr, pearsonr)

        np.random.seed(2)
        self.assertAlmostEqual(permutation_diff_test(corr_func, X, Y, Z, permute_both, False), 0.97002997002997, places=4)
        np.random.seed(2)
        self.assertAlmostEqual(permutation_diff_test(corr_func, Y, X, Z, permute_both, False), 0.030969030969030968, places=4)

    def test_williams_diff_test(self):
        # This test verifies that the output is the same as the psych package for
        # several different randomly generated inputs
        N, M = 9, 5
        corr_func = functools.partial(global_corr, pearsonr)

        np.random.seed(12)
        X = np.random.random((N, M))
        Y = np.random.random((N, M))
        Z = np.random.random((N, M))

        # These are used as input to r.test
        # effective_N = N * M
        # r12 = corr_func(X, Z)
        # r13 = corr_func(Y, Z)
        # r23 = corr_func(X, Y)

        # One tail
        expected_pvalue = 0.2716978
        actual_pvalue = williams_diff_test(corr_func, X, Y, Z, False)
        self.assertAlmostEqual(expected_pvalue, actual_pvalue, places=5)

        # The opposite order should produce 1-0.2716978. r.test does not do this and
        # will return 0.2716978 because it assumes that r12 > r13.
        actual_pvalue = williams_diff_test(corr_func, Y, X, Z, False)
        self.assertAlmostEqual(1.0 - expected_pvalue, actual_pvalue, places=5)

        # Two tails
        expected_pvalue = 0.5433956
        actual_pvalue = williams_diff_test(corr_func, X, Y, Z, True)
        self.assertAlmostEqual(expected_pvalue, actual_pvalue, places=5)

        # Should not matter the order for two tails
        actual_pvalue = williams_diff_test(corr_func, Y, X, Z, True)
        self.assertAlmostEqual(expected_pvalue, actual_pvalue, places=5)

        X = np.random.random((N, M))
        Y = np.random.random((N, M))
        Z = np.random.random((N, M))

        corr_func = functools.partial(system_level_corr, spearmanr)

        # These are used as input to r.test
        # effective_N = N
        # r12 = corr_func(X, Z)
        # r13 = corr_func(Y, Z)
        # r23 = corr_func(X, Y)

        # One tail
        # Since r12 < r13, r.test will only replicate this result with the reversed input order
        expected_pvalue = 0.4658712
        actual_pvalue = williams_diff_test(corr_func, Y, X, Z, False)
        self.assertAlmostEqual(expected_pvalue, actual_pvalue, places=5)

        # r.test would return the same result here, but we return 1.0 - expected
        actual_pvalue = williams_diff_test(corr_func, X, Y, Z, False)
        self.assertAlmostEqual(1.0 - expected_pvalue, actual_pvalue, places=5)

        # Two tails
        expected_pvalue = 0.9317423
        actual_pvalue = williams_diff_test(corr_func, X, Y, Z, True)
        self.assertAlmostEqual(expected_pvalue, actual_pvalue, places=5)

        # Order doesn't matter
        actual_pvalue = williams_diff_test(corr_func, Y, X, Z, True)
        self.assertAlmostEqual(expected_pvalue, actual_pvalue, places=5)