import numpy as np
import unittest

from sacrerouge.data import Metrics
from sacrerouge.stats import convert_to_matrices


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