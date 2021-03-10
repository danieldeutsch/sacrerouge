import numpy as np
import unittest
from scipy.stats import pearsonr

from sacrerouge.data import Metrics
from sacrerouge.stats import convert_to_matrices, summary_level_corr, system_level_corr, global_corr


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