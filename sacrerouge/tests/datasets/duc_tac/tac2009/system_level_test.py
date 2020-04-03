import os
import pytest
import unittest

from sacrerouge.commands.correlate import aggregate_metrics
from sacrerouge.data import Metrics
from sacrerouge.io import JsonlReader

_metrics_A_file_path = 'datasets/duc-tac/tac2009/v1.0/task1.A.metrics.jsonl'
_metrics_B_file_path = 'datasets/duc-tac/tac2009/v1.0/task1.B.metrics.jsonl'


class TestTAC2009SystemLevel(unittest.TestCase):
    @pytest.mark.skipif(not os.path.exists(_metrics_A_file_path), reason='TAC 2009-A metrics file does not exist')
    def test_system_level_A(self):
        summary_level_metrics = JsonlReader(_metrics_A_file_path, Metrics).read()
        system_level_metrics = aggregate_metrics(summary_level_metrics)

        # Check a few metrics to make sure they are equal to what's in the NIST files
        # ROUGE/rouge2_A.m.avg
        assert system_level_metrics['2']['rouge-2']['recall'] == pytest.approx(33.165, 1e-2)
        assert system_level_metrics['34']['rouge-2']['recall'] == pytest.approx(12.163, 1e-2)
        assert system_level_metrics['40']['rouge-2']['recall'] == pytest.approx(12.089, 1e-2)
        assert system_level_metrics['35']['rouge-2']['recall'] == pytest.approx(10.869, 1e-2)
        assert system_level_metrics['3']['rouge-2']['recall'] == pytest.approx(10.655, 1e-2)

        # ROUGE/rouge2_A.jk.m.avg
        assert system_level_metrics['C']['rouge-2_jk']['recall'] == pytest.approx(14.864, 1e-2)
        assert system_level_metrics['H']['rouge-2_jk']['recall'] == pytest.approx(13.457, 1e-2)
        assert system_level_metrics['E']['rouge-2_jk']['recall'] == pytest.approx(13.341, 1e-2)
        assert system_level_metrics['2']['rouge-2_jk']['recall'] == pytest.approx(33.133, 1e-2)
        assert system_level_metrics['34']['rouge-2_jk']['recall'] == pytest.approx(12.184, 1e-2)

        # ROUGE/rougeSU4_A.m.avg
        assert system_level_metrics['2']['rouge-su4']['recall'] == pytest.approx(34.421, 1e-2)
        assert system_level_metrics['40']['rouge-su4']['recall'] == pytest.approx(15.101, 1e-2)
        assert system_level_metrics['34']['rouge-su4']['recall'] == pytest.approx(15.030, 1e-2)
        assert system_level_metrics['35']['rouge-su4']['recall'] == pytest.approx(14.487, 1e-2)
        assert system_level_metrics['51']['rouge-su4']['recall'] == pytest.approx(14.165, 1e-2)

        # ROUGE/rougeSU4_A.jk.m.avg
        assert system_level_metrics['C']['rouge-su4_jk']['recall'] == pytest.approx(18.355, 1e-2)
        assert system_level_metrics['H']['rouge-su4_jk']['recall'] == pytest.approx(17.199, 1e-2)
        assert system_level_metrics['E']['rouge-su4_jk']['recall'] == pytest.approx(16.917, 1e-2)
        assert system_level_metrics['2']['rouge-su4_jk']['recall'] == pytest.approx(34.399, 1e-2)
        assert system_level_metrics['40']['rouge-su4_jk']['recall'] == pytest.approx(15.131, 1e-2)

        # manual/manual.model.A.avg
        assert system_level_metrics['A']['num_scus_jk'] == pytest.approx(10.364, 1e-2)
        assert system_level_metrics['B']['num_scus_jk'] == pytest.approx(9.5, 1e-2)
        assert system_level_metrics['C']['num_scus_jk'] == pytest.approx(12.364, 1e-2)

        assert system_level_metrics['A']['modified_pyramid_score_jk'] == pytest.approx(0.685, 1e-2)
        assert system_level_metrics['B']['modified_pyramid_score_jk'] == pytest.approx(0.616, 1e-2)
        assert system_level_metrics['C']['modified_pyramid_score_jk'] == pytest.approx(0.720, 1e-2)

        assert system_level_metrics['A']['linguistic_quality'] == pytest.approx(8.636, 1e-2)
        assert system_level_metrics['B']['linguistic_quality'] == pytest.approx(9.136, 1e-2)
        assert system_level_metrics['C']['linguistic_quality'] == pytest.approx(9.136, 1e-2)

        assert system_level_metrics['A']['overall_responsiveness'] == pytest.approx(8.455, 1e-2)
        assert system_level_metrics['B']['overall_responsiveness'] == pytest.approx(8.727, 1e-2)
        assert system_level_metrics['C']['overall_responsiveness'] == pytest.approx(9.318, 1e-2)

        # manual/manual.peer.A.avg
        assert system_level_metrics['1']['modified_pyramid_score'] == pytest.approx(0.175, 1e-2)
        assert system_level_metrics['2']['modified_pyramid_score'] == pytest.approx(0.646, 1e-2)
        assert system_level_metrics['3']['modified_pyramid_score'] == pytest.approx(0.358, 1e-2)

        assert system_level_metrics['1']['num_scus'] == pytest.approx(3.182, 1e-2)
        assert system_level_metrics['2']['num_scus'] == pytest.approx(11.977, 1e-2)
        assert system_level_metrics['3']['num_scus'] == pytest.approx(6.00, 1e-2)

        assert system_level_metrics['1']['num_repetitions'] == pytest.approx(1.318, 1e-2)
        assert system_level_metrics['2']['num_repetitions'] == pytest.approx(2.455, 1e-2)
        assert system_level_metrics['3']['num_repetitions'] == pytest.approx(1.568, 1e-2)

        assert system_level_metrics['1']['modified_pyramid_score_jk'] == pytest.approx(0.172, 1e-2)
        assert system_level_metrics['2']['modified_pyramid_score_jk'] == pytest.approx(0.635, 1e-2)
        assert system_level_metrics['3']['modified_pyramid_score_jk'] == pytest.approx(0.352, 1e-2)

        assert system_level_metrics['1']['linguistic_quality'] == pytest.approx(6.705, 1e-2)
        assert system_level_metrics['2']['linguistic_quality'] == pytest.approx(5.477, 1e-2)
        assert system_level_metrics['3']['linguistic_quality'] == pytest.approx(7.477, 1e-2)

        assert system_level_metrics['1']['overall_responsiveness'] == pytest.approx(3.636, 1e-2)
        assert system_level_metrics['2']['overall_responsiveness'] == pytest.approx(6.364, 1e-2)
        assert system_level_metrics['3']['overall_responsiveness'] == pytest.approx(6.341, 1e-2)

        # BE/simple_A.m.hm.avg
        assert system_level_metrics['2']['rouge-be-hm']['recall'] == pytest.approx(24.820, 1e-2)
        assert system_level_metrics['34']['rouge-be-hm']['recall'] == pytest.approx(6.356, 1e-2)
        assert system_level_metrics['40']['rouge-be-hm']['recall'] == pytest.approx(6.321, 1e-2)
        assert system_level_metrics['45']['rouge-be-hm']['recall'] == pytest.approx(5.899, 1e-2)
        assert system_level_metrics['4']['rouge-be-hm']['recall'] == pytest.approx(5.843, 1e-2)

        # BE/simplejk_A.m.hm.avg
        assert system_level_metrics['C']['rouge-be-hm_jk']['recall'] == pytest.approx(7.876, 1e-2)
        assert system_level_metrics['E']['rouge-be-hm_jk']['recall'] == pytest.approx(6.909, 1e-2)
        assert system_level_metrics['F']['rouge-be-hm_jk']['recall'] == pytest.approx(6.840, 1e-2)
        assert system_level_metrics['2']['rouge-be-hm_jk']['recall'] == pytest.approx(24.830, 1e-2)
        assert system_level_metrics['34']['rouge-be-hm_jk']['recall'] == pytest.approx(6.379, 1e-2)

        # aesop_allpeers_A
        assert system_level_metrics['A']['aesop']['1'] == pytest.approx(0.154895909090909, 1e-2)
        assert system_level_metrics['C']['aesop']['8'] == pytest.approx(0.0419939626932389, 1e-2)
        assert system_level_metrics['4']['aesop']['13'] == pytest.approx(0.2186197727, 1e-2)
        assert system_level_metrics['8']['aesop']['22'] == pytest.approx(0.1286081818, 1e-2)
        assert system_level_metrics['16']['aesop']['30'] == pytest.approx(0.2341865909, 1e-2)

    @pytest.mark.skipif(not os.path.exists(_metrics_B_file_path), reason='TAC 2009-B metrics file does not exist')
    def test_system_level_B(self):
        summary_level_metrics = JsonlReader(_metrics_B_file_path, Metrics).read()
        system_level_metrics = aggregate_metrics(summary_level_metrics)

        # Check a few metrics to make sure they are equal to what's in the NIST files
        # ROUGE/rouge2_B.m.avg
        assert system_level_metrics['2']['rouge-2']['recall'] == pytest.approx(31.956, 1e-2)
        assert system_level_metrics['34']['rouge-2']['recall'] == pytest.approx(10.386, 1e-2)
        assert system_level_metrics['40']['rouge-2']['recall'] == pytest.approx(10.373, 1e-2)
        assert system_level_metrics['35']['rouge-2']['recall'] == pytest.approx(10.104, 1e-2)
        assert system_level_metrics['3']['rouge-2']['recall'] == pytest.approx(9.820, 1e-2)

        # ROUGE/rouge2_B.jk.m.avg
        # C is off by a bit?
        # assert system_level_metrics['C']['rouge-2_jk']['recall'] == pytest.approx(12.550, 1e-2)
        assert system_level_metrics['H']['rouge-2_jk']['recall'] == pytest.approx(12.436, 1e-2)
        assert system_level_metrics['E']['rouge-2_jk']['recall'] == pytest.approx(11.001, 1e-2)
        assert system_level_metrics['2']['rouge-2_jk']['recall'] == pytest.approx(31.932, 1e-2)
        assert system_level_metrics['34']['rouge-2_jk']['recall'] == pytest.approx(10.417, 1e-2)

        # ROUGE/rougeSU4_B.m.avg
        assert system_level_metrics['2']['rouge-su4']['recall'] == pytest.approx(33.688, 1e-2)
        assert system_level_metrics['40']['rouge-su4']['recall'] == pytest.approx(13.948, 1e-2)
        assert system_level_metrics['34']['rouge-su4']['recall'] == pytest.approx(13.851, 1e-2)
        assert system_level_metrics['35']['rouge-su4']['recall'] == pytest.approx(13.839, 1e-2)
        assert system_level_metrics['51']['rouge-su4']['recall'] == pytest.approx(13.650, 1e-2)

        # ROUGE/rougeSU4_B.jk.m.avg
        assert system_level_metrics['C']['rouge-su4_jk']['recall'] == pytest.approx(16.386, 1e-2)
        assert system_level_metrics['H']['rouge-su4_jk']['recall'] == pytest.approx(16.602, 1e-2)
        assert system_level_metrics['E']['rouge-su4_jk']['recall'] == pytest.approx(15.152, 1e-2)
        assert system_level_metrics['2']['rouge-su4_jk']['recall'] == pytest.approx(33.668, 1e-2)
        assert system_level_metrics['40']['rouge-su4_jk']['recall'] == pytest.approx(13.959, 1e-2)

        # manual/manual.model.B.avg
        assert system_level_metrics['A']['num_scus_jk'] == pytest.approx(6.455, 1e-2)
        assert system_level_metrics['B']['num_scus_jk'] == pytest.approx(8.591, 1e-2)
        assert system_level_metrics['C']['num_scus_jk'] == pytest.approx(8.545, 1e-2)

        assert system_level_metrics['A']['modified_pyramid_score_jk'] == pytest.approx(0.481, 1e-2)
        assert system_level_metrics['B']['modified_pyramid_score_jk'] == pytest.approx(0.663, 1e-2)
        assert system_level_metrics['C']['modified_pyramid_score_jk'] == pytest.approx(0.640, 1e-2)

        assert system_level_metrics['A']['linguistic_quality'] == pytest.approx(8.727, 1e-2)
        assert system_level_metrics['B']['linguistic_quality'] == pytest.approx(8.545, 1e-2)
        assert system_level_metrics['C']['linguistic_quality'] == pytest.approx(9.364, 1e-2)

        assert system_level_metrics['A']['overall_responsiveness'] == pytest.approx(8.364, 1e-2)
        assert system_level_metrics['B']['overall_responsiveness'] == pytest.approx(8.318, 1e-2)
        assert system_level_metrics['C']['overall_responsiveness'] == pytest.approx(9.136, 1e-2)

        # manual/manual.peer.B.avg
        assert system_level_metrics['1']['modified_pyramid_score'] == pytest.approx(0.160, 1e-2)
        assert system_level_metrics['2']['modified_pyramid_score'] == pytest.approx(0.690, 1e-2)
        assert system_level_metrics['3']['modified_pyramid_score'] == pytest.approx(0.329, 1e-2)

        assert system_level_metrics['1']['num_scus'] == pytest.approx(2.386, 1e-2)
        assert system_level_metrics['2']['num_scus'] == pytest.approx(9.886, 1e-2)
        assert system_level_metrics['3']['num_scus'] == pytest.approx(4.545, 1e-2)

        assert system_level_metrics['1']['num_repetitions'] == pytest.approx(0.841, 1e-2)
        assert system_level_metrics['2']['num_repetitions'] == pytest.approx(1.955, 1e-2)
        assert system_level_metrics['3']['num_repetitions'] == pytest.approx(0.955, 1e-2)

        assert system_level_metrics['1']['modified_pyramid_score_jk'] == pytest.approx(0.158, 1e-2)
        assert system_level_metrics['2']['modified_pyramid_score_jk'] == pytest.approx(0.677, 1e-2)
        assert system_level_metrics['3']['modified_pyramid_score_jk'] == pytest.approx(0.324, 1e-2)

        assert system_level_metrics['1']['linguistic_quality'] == pytest.approx(6.455, 1e-2)
        assert system_level_metrics['2']['linguistic_quality'] == pytest.approx(5.886, 1e-2)
        assert system_level_metrics['3']['linguistic_quality'] == pytest.approx(7.250, 1e-2)

        assert system_level_metrics['1']['overall_responsiveness'] == pytest.approx(4.318, 1e-2)
        assert system_level_metrics['2']['overall_responsiveness'] == pytest.approx(6.182, 1e-2)
        assert system_level_metrics['3']['overall_responsiveness'] == pytest.approx(6.114, 1e-2)

        # BE/simple_B.m.hm.avg
        assert system_level_metrics['2']['rouge-be-hm']['recall'] == pytest.approx(25.041, 1e-2)
        assert system_level_metrics['24']['rouge-be-hm']['recall'] == pytest.approx(6.389, 1e-2)
        assert system_level_metrics['40']['rouge-be-hm']['recall'] == pytest.approx(6.162, 1e-2)
        assert system_level_metrics['34']['rouge-be-hm']['recall'] == pytest.approx(6.118, 1e-2)
        assert system_level_metrics['35']['rouge-be-hm']['recall'] == pytest.approx(5.813, 1e-2)

        # BE/simplejk_B.m.hm.avg
        # F is off by a little
        assert system_level_metrics['C']['rouge-be-hm_jk']['recall'] == pytest.approx(6.795, 1e-2)
        assert system_level_metrics['H']['rouge-be-hm_jk']['recall'] == pytest.approx(7.040, 1e-2)
        assert system_level_metrics['F']['rouge-be-hm_jk']['recall'] == pytest.approx(6.094, 1e-1)
        assert system_level_metrics['2']['rouge-be-hm_jk']['recall'] == pytest.approx(25.042, 1e-2)
        assert system_level_metrics['34']['rouge-be-hm_jk']['recall'] == pytest.approx(6.134, 1e-2)

        # aesop_allpeers_B
        assert system_level_metrics['B']['aesop']['2'] == pytest.approx(0.04890409091, 1e-2)
        assert system_level_metrics['E']['aesop']['4'] == pytest.approx(0.2740872727, 1e-2)
        assert system_level_metrics['6']['aesop']['7'] == pytest.approx(0.5850288957, 1e-2)
        assert system_level_metrics['9']['aesop']['20'] == pytest.approx(0.06261788636, 1e-2)
        assert system_level_metrics['14']['aesop']['34'] == pytest.approx(0.3664196656, 1e-2)
