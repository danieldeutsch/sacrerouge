import os
import pytest
import unittest

from sacrerouge.commands.correlate import aggregate_metrics
from sacrerouge.data import Metrics
from sacrerouge.io import JsonlReader

_metrics_file_path = 'datasets/duc-tac/tac2008/v1.0/task1.A-B.metrics.jsonl'


class TestTAC2008SystemLevel(unittest.TestCase):
    @pytest.mark.skipif(not os.path.exists(_metrics_file_path), reason='TAC 2008 metrics file does not exist')
    def test_system_level(self):
        summary_level_metrics = JsonlReader(_metrics_file_path, Metrics).read()
        system_level_metrics = aggregate_metrics(summary_level_metrics)

        # Check a few metrics to make sure they are equal to what's in the NIST files
        # ROUGE/rouge2.m.avg
        assert system_level_metrics['43']['rouge-2']['recall'] == pytest.approx(10.382, 1e-2)
        assert system_level_metrics['13']['rouge-2']['recall'] == pytest.approx(9.900, 1e-2)
        assert system_level_metrics['14']['rouge-2']['recall'] == pytest.approx(9.773, 1e-2)
        assert system_level_metrics['2']['rouge-2']['recall'] == pytest.approx(9.610, 1e-2)
        assert system_level_metrics['65']['rouge-2']['recall'] == pytest.approx(9.558, 1e-2)

        # ROUGE/rouge2.jk.m.avg
        assert system_level_metrics['D']['rouge-2_jk']['recall'] == pytest.approx(13.197, 1e-2)
        assert system_level_metrics['F']['rouge-2_jk']['recall'] == pytest.approx(12.896, 1e-2)
        assert system_level_metrics['H']['rouge-2_jk']['recall'] == pytest.approx(12.010, 1e-2)
        assert system_level_metrics['43']['rouge-2_jk']['recall'] == pytest.approx(10.395, 1e-2)
        assert system_level_metrics['13']['rouge-2_jk']['recall'] == pytest.approx(9.901, 1e-2)

        # ROUGE/rougeSU4.m.avg
        assert system_level_metrics['43']['rouge-su4']['recall'] == pytest.approx(13.625, 1e-2)
        assert system_level_metrics['37']['rouge-su4']['recall'] == pytest.approx(13.574, 1e-2)
        assert system_level_metrics['60']['rouge-su4']['recall'] == pytest.approx(13.570, 1e-2)
        assert system_level_metrics['2']['rouge-su4']['recall'] == pytest.approx(13.419, 1e-2)
        assert system_level_metrics['14']['rouge-su4']['recall'] == pytest.approx(13.283, 1e-2)

        # ROUGE/rougeSU4.jk.m.avg
        assert system_level_metrics['D']['rouge-su4_jk']['recall'] == pytest.approx(16.878, 1e-2)
        assert system_level_metrics['F']['rouge-su4_jk']['recall'] == pytest.approx(16.490, 1e-2)
        assert system_level_metrics['H']['rouge-su4_jk']['recall'] == pytest.approx(15.565, 1e-2)
        assert system_level_metrics['43']['rouge-su4_jk']['recall'] == pytest.approx(13.646, 1e-2)
        assert system_level_metrics['37']['rouge-su4_jk']['recall'] == pytest.approx(13.592, 1e-2)

        # manual/manual.model.avg
        assert system_level_metrics['A']['num_scus_jk'] == pytest.approx(8.021, 1e-2)
        assert system_level_metrics['B']['num_scus_jk'] == pytest.approx(8.479, 1e-2)
        assert system_level_metrics['C']['num_scus_jk'] == pytest.approx(8.208, 1e-2)

        assert system_level_metrics['A']['modified_pyramid_score_jk'] == pytest.approx(0.608, 1e-2)
        assert system_level_metrics['B']['modified_pyramid_score_jk'] == pytest.approx(0.625, 1e-2)
        assert system_level_metrics['C']['modified_pyramid_score_jk'] == pytest.approx(0.651, 1e-2)

        assert system_level_metrics['A']['linguistic_quality'] == pytest.approx(4.833, 1e-2)
        assert system_level_metrics['B']['linguistic_quality'] == pytest.approx(4.812, 1e-2)
        assert system_level_metrics['C']['linguistic_quality'] == pytest.approx(4.604, 1e-2)

        assert system_level_metrics['A']['overall_responsiveness'] == pytest.approx(4.688, 1e-2)
        assert system_level_metrics['B']['overall_responsiveness'] == pytest.approx(4.583, 1e-2)
        assert system_level_metrics['C']['overall_responsiveness'] == pytest.approx(4.500, 1e-2)

        # manual/manual.peer.avg
        assert system_level_metrics['0']['modified_pyramid_score'] == pytest.approx(0.166, 1e-2)
        assert system_level_metrics['1']['modified_pyramid_score'] == pytest.approx(0.265, 1e-2)
        assert system_level_metrics['2']['modified_pyramid_score'] == pytest.approx(0.280, 1e-2)

        assert system_level_metrics['0']['num_scus'] == pytest.approx(2.635, 1e-2)
        assert system_level_metrics['1']['num_scus'] == pytest.approx(3.854, 1e-2)
        assert system_level_metrics['2']['num_scus'] == pytest.approx(4.000, 1e-2)

        assert system_level_metrics['0']['num_repetitions'] == pytest.approx(0.688, 1e-2)
        assert system_level_metrics['1']['num_repetitions'] == pytest.approx(0.885, 1e-2)
        assert system_level_metrics['2']['num_repetitions'] == pytest.approx(1.156, 1e-2)

        assert system_level_metrics['0']['modified_pyramid_score_jk'] == pytest.approx(0.163, 1e-2)
        assert system_level_metrics['1']['modified_pyramid_score_jk'] == pytest.approx(0.261, 1e-2)
        assert system_level_metrics['2']['modified_pyramid_score_jk'] == pytest.approx(0.276, 1e-2)

        assert system_level_metrics['0']['linguistic_quality'] == pytest.approx(3.333, 1e-2)
        assert system_level_metrics['1']['linguistic_quality'] == pytest.approx(2.719, 1e-2)
        assert system_level_metrics['2']['linguistic_quality'] == pytest.approx(2.354, 1e-2)

        assert system_level_metrics['0']['overall_responsiveness'] == pytest.approx(2.073, 1e-2)
        assert system_level_metrics['1']['overall_responsiveness'] == pytest.approx(2.427, 1e-2)
        assert system_level_metrics['2']['overall_responsiveness'] == pytest.approx(2.385, 1e-2)

        # BE/simple.m.hm.avg
        assert system_level_metrics['14']['rouge-be-hm']['recall'] == pytest.approx(6.462, 1e-2)
        assert system_level_metrics['65']['rouge-be-hm']['recall'] == pytest.approx(6.276, 1e-2)
        assert system_level_metrics['43']['rouge-be-hm']['recall'] == pytest.approx(6.257, 1e-2)
        assert system_level_metrics['49']['rouge-be-hm']['recall'] == pytest.approx(6.247, 1e-2)
        assert system_level_metrics['60']['rouge-be-hm']['recall'] == pytest.approx(6.198, 1e-2)

        # BE/simple.jk.m.hm.avg
        assert system_level_metrics['D']['rouge-be-hm_jk']['recall'] == pytest.approx(9.959, 1e-2)
        assert system_level_metrics['F']['rouge-be-hm_jk']['recall'] == pytest.approx(9.553, 1e-2)
        assert system_level_metrics['G']['rouge-be-hm_jk']['recall'] == pytest.approx(9.154, 1e-2)
        assert system_level_metrics['14']['rouge-be-hm_jk']['recall'] == pytest.approx(6.480, 1e-2)
        assert system_level_metrics['65']['rouge-be-hm_jk']['recall'] == pytest.approx(6.293, 1e-2)
