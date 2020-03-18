import os
import pytest
import unittest

from sacrerouge.compute_correlation import aggregate_metrics
from sacrerouge.io import JsonlReader

_task1_metrics_file_path = 'datasets/duc-tac/duc2007/v1.0/task1.metrics.jsonl'
_task2_metrics_file_path = 'datasets/duc-tac/duc2007/v1.0/task2.A-B-C.metrics.jsonl'


class TestDUC2007SystemLevel(unittest.TestCase):
    @pytest.mark.skipif(not os.path.exists(_task1_metrics_file_path), reason='DUC 2007 task 1 metrics file does not exist')
    def test_task1_system_level(self):
        summary_level_metrics = JsonlReader(_task1_metrics_file_path).read()
        system_level_metrics = aggregate_metrics(summary_level_metrics, 'summarizer_id')

        # Check a few metrics to make sure they are equal to what's in the NIST files
        # mainEval/ROUGE/rouge2.jk.m.avg
        assert system_level_metrics['D']['rouge-2_jk']['recall'] == pytest.approx(17.528, 1e-2)
        assert system_level_metrics['C']['rouge-2_jk']['recall'] == pytest.approx(15.055, 1e-2)
        assert system_level_metrics['B']['rouge-2_jk']['recall'] == pytest.approx(13.992, 1e-2)
        assert system_level_metrics['15']['rouge-2_jk']['recall'] == pytest.approx(12.448, 1e-2)
        assert system_level_metrics['29']['rouge-2_jk']['recall'] == pytest.approx(12.028, 1e-2)

        # mainEval/ROUGE/rougeSU4.jk.m.avg
        assert system_level_metrics['D']['rouge-su4_jk']['recall'] == pytest.approx(21.892, 1e-2)
        assert system_level_metrics['C']['rouge-su4_jk']['recall'] == pytest.approx(19.921, 1e-2)
        assert system_level_metrics['E']['rouge-su4_jk']['recall'] == pytest.approx(19.396, 1e-2)
        assert system_level_metrics['15']['rouge-su4_jk']['recall'] == pytest.approx(17.711, 1e-2)
        assert system_level_metrics['24']['rouge-su4_jk']['recall'] == pytest.approx(17.593, 1e-2)

        # mainEval/manual/avg_content
        assert system_level_metrics['D']['content_responsiveness'] == pytest.approx(4.944, 1e-2)
        assert system_level_metrics['I']['content_responsiveness'] == pytest.approx(4.889, 1e-2)
        assert system_level_metrics['G']['content_responsiveness'] == pytest.approx(4.889, 1e-2)
        assert system_level_metrics['4']['content_responsiveness'] == pytest.approx(3.400, 1e-2)
        assert system_level_metrics['23']['content_responsiveness'] == pytest.approx(3.311, 1e-2)

        # mainEval/BE/simple.jk.m.hm.avg
        assert system_level_metrics['D']['rouge-be-hm_jk']['recall'] == pytest.approx(12.284, 1e-2)
        assert system_level_metrics['C']['rouge-be-hm_jk']['recall'] == pytest.approx(9.593, 1e-2)
        assert system_level_metrics['B']['rouge-be-hm_jk']['recall'] == pytest.approx(9.146, 1e-2)
        assert system_level_metrics['15']['rouge-be-hm_jk']['recall'] == pytest.approx(6.632, 1e-2)
        assert system_level_metrics['24']['rouge-be-hm_jk']['recall'] == pytest.approx(6.577, 1e-2)

    @pytest.mark.skipif(not os.path.exists(_task2_metrics_file_path), reason='DUC 2007 task 2 metrics file does not exist')
    def test_task2_system_level(self):
        summary_level_metrics = JsonlReader(_task2_metrics_file_path).read()
        system_level_metrics = aggregate_metrics(summary_level_metrics, 'summarizer_id')

        # Check a few metrics to make sure they are equal to what's in the NIST files
        # updateEval/ROUGE/rouge2.jk.m.avg
        assert system_level_metrics['D']['rouge-2_jk']['recall'] == pytest.approx(14.499, 1e-2)
        assert system_level_metrics['C']['rouge-2_jk']['recall'] == pytest.approx(14.330, 1e-2)
        assert system_level_metrics['G']['rouge-2_jk']['recall'] == pytest.approx(13.942, 1e-2)
        assert system_level_metrics['40']['rouge-2_jk']['recall'] == pytest.approx(11.189, 1e-2)
        assert system_level_metrics['55']['rouge-2_jk']['recall'] == pytest.approx(9.851, 1e-2)

        # updateEval/ROUGE/rougeSU4.jk.m.avg
        assert system_level_metrics['D']['rouge-su4_jk']['recall'] == pytest.approx(17.998, 1e-2)
        assert system_level_metrics['C']['rouge-su4_jk']['recall'] == pytest.approx(17.923, 1e-2)
        assert system_level_metrics['E']['rouge-su4_jk']['recall'] == pytest.approx(17.689, 1e-2)
        assert system_level_metrics['40']['rouge-su4_jk']['recall'] == pytest.approx(14.306, 1e-2)
        assert system_level_metrics['44']['rouge-su4_jk']['recall'] == pytest.approx(13.607, 1e-2)

        # updateEval/manual/Responsiveness/avg_content.all
        assert system_level_metrics['D']['content_responsiveness'] == pytest.approx(4.833, 1e-2)
        assert system_level_metrics['C']['content_responsiveness'] == pytest.approx(4.833, 1e-2)
        assert system_level_metrics['E']['content_responsiveness'] == pytest.approx(4.750, 1e-2)
        assert system_level_metrics['40']['content_responsiveness'] == pytest.approx(2.967, 1e-2)
        assert system_level_metrics['36']['content_responsiveness'] == pytest.approx(2.800, 1e-2)

        # updateEval/BE/simple.jk.m.hm.avg
        assert system_level_metrics['D']['rouge-be-hm_jk']['recall'] == pytest.approx(10.687, 1e-2)
        assert system_level_metrics['C']['rouge-be-hm_jk']['recall'] == pytest.approx(10.214, 1e-2)
        assert system_level_metrics['E']['rouge-be-hm_jk']['recall'] == pytest.approx(10.177, 1e-2)
        assert system_level_metrics['40']['rouge-be-hm_jk']['recall'] == pytest.approx(7.219, 1e-2)
        assert system_level_metrics['44']['rouge-be-hm_jk']['recall'] == pytest.approx(5.544, 1e-2)
