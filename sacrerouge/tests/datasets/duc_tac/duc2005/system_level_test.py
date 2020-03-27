import os
import pytest
import unittest

from sacrerouge.compute_correlation import aggregate_metrics
from sacrerouge.data import Metrics
from sacrerouge.io import JsonlReader

_metrics_file_path = 'datasets/duc-tac/duc2005/v1.0/task1.metrics.jsonl'


class TestDUC2005SystemLevel(unittest.TestCase):
    @pytest.mark.skipif(not os.path.exists(_metrics_file_path), reason='DUC 2005 metrics file does not exist')
    def test_system_level(self):
        summary_level_metrics = JsonlReader(_metrics_file_path, Metrics).read()
        system_level_metrics = aggregate_metrics(summary_level_metrics)

        # Check a few metrics to make sure they are equal to what's in the NIST files
        # ROUGE/rouge2.jk.m.avg
        assert system_level_metrics['32']['rouge-1_jk']['recall'] == pytest.approx(32.4835488888889, 1e-2)
        assert system_level_metrics['32']['rouge-1_jk']['precision'] == pytest.approx(33.3402216666667, 1e-2)
        assert system_level_metrics['21']['rouge-2_jk']['recall'] == pytest.approx(5.72633166666666, 1e-2)
        assert system_level_metrics['21']['rouge-2_jk']['precision'] == pytest.approx(5.70379111111111, 1e-2)
        assert system_level_metrics['E']['rouge-2_jk']['recall'] == pytest.approx(10.5482258064516, 1e-2)
        assert system_level_metrics['E']['rouge-2_jk']['precision'] == pytest.approx(11.9319677419355, 1e-2)

        # ROUGE/rougeSU4.jk.m.avg
        assert system_level_metrics['H']['rouge-su4_jk']['recall'] == pytest.approx(14.8429, 1e-2)
        assert system_level_metrics['F']['rouge-su4_jk']['recall'] == pytest.approx(15.8717666666667, 1e-2)
        assert system_level_metrics['E']['rouge-su4_jk']['recall'] == pytest.approx(15.9369677419355, 1e-2)
        assert system_level_metrics['23']['rouge-su4_jk']['recall'] == pytest.approx(5.56854166666667, 1e-2)
        assert system_level_metrics['1']['rouge-su4_jk']['recall'] == pytest.approx(8.71616333333333, 1e-2)

        # Not checking responsiveness because they implemented a scaled responsiveness which
        # we did not do here
