import os
import pytest
import unittest

from sacrerouge.compute_correlation import aggregate_metrics
from sacrerouge.data import Metrics
from sacrerouge.io import JsonlReader

_metrics_file_path = 'datasets/duc-tac/duc2006/v1.0/task1.metrics.jsonl'


class TestDUC2006SystemLevel(unittest.TestCase):
    @pytest.mark.skipif(not os.path.exists(_metrics_file_path), reason='DUC 2006 metrics file does not exist')
    def test_system_level(self):
        summary_level_metrics = JsonlReader(_metrics_file_path, Metrics).read()
        system_level_metrics = aggregate_metrics(summary_level_metrics)

        # Check a few metrics to make sure they are equal to what's in the NIST files
        # NISTeval2/ROUGE/rouge2.jk.m.avg
        assert system_level_metrics['C']['rouge-2_jk']['recall'] == pytest.approx(13.260, 1e-2)
        assert system_level_metrics['D']['rouge-2_jk']['recall'] == pytest.approx(12.380, 1e-2)
        assert system_level_metrics['B']['rouge-2_jk']['recall'] == pytest.approx(11.788, 1e-2)
        assert system_level_metrics['24']['rouge-2_jk']['recall'] == pytest.approx(9.558, 1e-2)
        assert system_level_metrics['15']['rouge-2_jk']['recall'] == pytest.approx(9.097, 1e-2)

        # NISTeval2/ROUGE/rougeSU4.jk.m.avg
        assert system_level_metrics['C']['rouge-su4_jk']['recall'] == pytest.approx(18.385, 1e-2)
        assert system_level_metrics['D']['rouge-su4_jk']['recall'] == pytest.approx(17.814, 1e-2)
        assert system_level_metrics['B']['rouge-su4_jk']['recall'] == pytest.approx(17.665, 1e-2)
        assert system_level_metrics['24']['rouge-su4_jk']['recall'] == pytest.approx(15.529, 1e-2)
        assert system_level_metrics['12']['rouge-su4_jk']['recall'] == pytest.approx(14.755, 1e-2)

        # NISTeval/responsiveness/avg_content
        assert system_level_metrics['D']['content_responsiveness'] == pytest.approx(4.9, 1e-2)
        assert system_level_metrics['C']['content_responsiveness'] == pytest.approx(4.9, 1e-2)
        assert system_level_metrics['B']['content_responsiveness'] == pytest.approx(4.9, 1e-2)
        assert system_level_metrics['27']['content_responsiveness'] == pytest.approx(3.08, 1e-2)
        assert system_level_metrics['23']['content_responsiveness'] == pytest.approx(3.0, 1e-2)

        # NISTeval/responsiveness/avg_overall
        assert system_level_metrics['E']['overall_responsiveness'] == pytest.approx(4.9, 1e-2)
        assert system_level_metrics['D']['overall_responsiveness'] == pytest.approx(4.9, 1e-2)
        assert system_level_metrics['I']['overall_responsiveness'] == pytest.approx(4.8, 1e-2)
        assert system_level_metrics['27']['overall_responsiveness'] == pytest.approx(2.84, 1e-2)
        assert system_level_metrics['23']['overall_responsiveness'] == pytest.approx(2.76, 1e-2)

        # NISTeval2/BE/simple.jk.m.hm.avg
        assert system_level_metrics['C']['rouge-be-hm_jk']['recall'] == pytest.approx(9.905, 1e-2)
        assert system_level_metrics['B']['rouge-be-hm_jk']['recall'] == pytest.approx(7.847, 1e-2)
        assert system_level_metrics['D']['rouge-be-hm_jk']['recall'] == pytest.approx(7.466, 1e-2)
        assert system_level_metrics['24']['rouge-be-hm_jk']['recall'] == pytest.approx(5.107, 1e-2)
        assert system_level_metrics['23']['rouge-be-hm_jk']['recall'] == pytest.approx(5.049, 1e-2)
