import os
import pytest
import unittest

from sacrerouge.compute_correlation import aggregate_metrics
from sacrerouge.data import Metrics
from sacrerouge.io import JsonlReader

_metrics_A_file_path = 'datasets/duc-tac/tac2010/v1.0/task1.A.metrics.jsonl'
_metrics_B_file_path = 'datasets/duc-tac/tac2010/v1.0/task1.B.metrics.jsonl'


class TestTAC2010SystemLevel(unittest.TestCase):
    @pytest.mark.skipif(not os.path.exists(_metrics_A_file_path), reason='TAC 2010-A metrics file does not exist')
    def test_system_level_A(self):
        summary_level_metrics = JsonlReader(_metrics_A_file_path, Metrics).read()
        system_level_metrics = aggregate_metrics(summary_level_metrics)

        # Check a few metrics to make sure they are equal to what's in the NIST files
        # ROUGE/rouge2_A.m.avg
        assert system_level_metrics['22']['rouge-2']['recall'] == pytest.approx(9.574, 1e-2)
        assert system_level_metrics['18']['rouge-2']['recall'] == pytest.approx(9.418, 1e-2)
        assert system_level_metrics['23']['rouge-2']['recall'] == pytest.approx(9.404, 1e-2)
        assert system_level_metrics['24']['rouge-2']['recall'] == pytest.approx(9.196, 1e-2)
        assert system_level_metrics['36']['rouge-2']['recall'] == pytest.approx(9.194, 1e-2)

        # ROUGE/rouge2_A.jk.m.avg
        assert system_level_metrics['D']['rouge-2_jk']['recall'] == pytest.approx(12.862, 1e-2)
        assert system_level_metrics['H']['rouge-2_jk']['recall'] == pytest.approx(12.841, 1e-1)
        assert system_level_metrics['F']['rouge-2_jk']['recall'] == pytest.approx(12.556, 1e-2)
        assert system_level_metrics['22']['rouge-2_jk']['recall'] == pytest.approx(9.620, 1e-2)
        assert system_level_metrics['18']['rouge-2_jk']['recall'] == pytest.approx(9.451, 1e-2)

        # ROUGE/rougeSU4_A.m.avg
        assert system_level_metrics['22']['rouge-su4']['recall'] == pytest.approx(13.014, 1e-2)
        assert system_level_metrics['23']['rouge-su4']['recall'] == pytest.approx(12.963, 1e-2)
        assert system_level_metrics['24']['rouge-su4']['recall'] == pytest.approx(12.829, 1e-2)
        assert system_level_metrics['18']['rouge-su4']['recall'] == pytest.approx(12.407, 1e-2)
        assert system_level_metrics['34']['rouge-su4']['recall'] == pytest.approx(12.283, 1e-2)

        # ROUGE/rougeSU4_A.jk.m.avg
        assert system_level_metrics['H']['rouge-su4_jk']['recall'] == pytest.approx(16.294, 1e-2)
        assert system_level_metrics['F']['rouge-su4_jk']['recall'] == pytest.approx(16.212, 1e-2)
        assert system_level_metrics['D']['rouge-su4_jk']['recall'] == pytest.approx(16.200, 1e-2)
        assert system_level_metrics['22']['rouge-su4_jk']['recall'] == pytest.approx(13.049, 1e-2)
        assert system_level_metrics['23']['rouge-su4_jk']['recall'] == pytest.approx(12.978, 1e-2)

        # manual/manual.model.A.avg
        assert system_level_metrics['A']['num_scus_jk'] == pytest.approx(10.870, 1e-2)
        assert system_level_metrics['B']['num_scus_jk'] == pytest.approx(11.087, 1e-2)
        assert system_level_metrics['C']['num_scus_jk'] == pytest.approx(9.826, 1e-2)

        assert system_level_metrics['A']['modified_pyramid_score_jk'] == pytest.approx(0.779, 1e-2)
        assert system_level_metrics['B']['modified_pyramid_score_jk'] == pytest.approx(0.747, 1e-2)
        assert system_level_metrics['C']['modified_pyramid_score_jk'] == pytest.approx(0.661, 1e-2)

        assert system_level_metrics['A']['linguistic_quality'] == pytest.approx(4.913, 1e-2)
        assert system_level_metrics['B']['linguistic_quality'] == pytest.approx(4.870, 1e-2)
        assert system_level_metrics['C']['linguistic_quality'] == pytest.approx(4.826, 1e-2)

        assert system_level_metrics['A']['overall_responsiveness'] == pytest.approx(4.783, 1e-2)
        assert system_level_metrics['B']['overall_responsiveness'] == pytest.approx(4.696, 1e-2)
        assert system_level_metrics['C']['overall_responsiveness'] == pytest.approx(4.565, 1e-2)

        # manual/manual.peer.A.avg
        assert system_level_metrics['1']['modified_pyramid_score'] == pytest.approx(0.233, 1e-2)
        assert system_level_metrics['2']['modified_pyramid_score'] == pytest.approx(0.296, 1e-2)
        assert system_level_metrics['3']['modified_pyramid_score'] == pytest.approx(0.399, 1e-2)

        assert system_level_metrics['1']['num_scus'] == pytest.approx(3.304, 1e-2)
        assert system_level_metrics['2']['num_scus'] == pytest.approx(4.217, 1e-2)
        assert system_level_metrics['3']['num_scus'] == pytest.approx(5.500, 1e-2)

        assert system_level_metrics['1']['num_repetitions'] == pytest.approx(0.522, 1e-2)
        assert system_level_metrics['2']['num_repetitions'] == pytest.approx(1.217, 1e-2)
        assert system_level_metrics['3']['num_repetitions'] == pytest.approx(1.413, 1e-2)

        assert system_level_metrics['1']['modified_pyramid_score_jk'] == pytest.approx(0.229, 1e-2)
        assert system_level_metrics['2']['modified_pyramid_score_jk'] == pytest.approx(0.291, 1e-2)
        assert system_level_metrics['3']['modified_pyramid_score_jk'] == pytest.approx(0.393, 1e-2)

        assert system_level_metrics['1']['linguistic_quality'] == pytest.approx(3.652, 1e-2)
        assert system_level_metrics['2']['linguistic_quality'] == pytest.approx(2.717, 1e-2)
        assert system_level_metrics['3']['linguistic_quality'] == pytest.approx(3.043, 1e-2)

        assert system_level_metrics['1']['overall_responsiveness'] == pytest.approx(2.174, 1e-2)
        assert system_level_metrics['2']['overall_responsiveness'] == pytest.approx(2.500, 1e-2)
        assert system_level_metrics['3']['overall_responsiveness'] == pytest.approx(2.978, 1e-2)

        # BE/simple_A.m.hm.avg
        assert system_level_metrics['22']['rouge-be-hm']['recall'] == pytest.approx(5.937, 1e-2)
        assert system_level_metrics['23']['rouge-be-hm']['recall'] == pytest.approx(5.809, 1e-2)
        assert system_level_metrics['18']['rouge-be-hm']['recall'] == pytest.approx(5.749, 1e-2)
        assert system_level_metrics['13']['rouge-be-hm']['recall'] == pytest.approx(5.553, 1e-2)
        assert system_level_metrics['16']['rouge-be-hm']['recall'] == pytest.approx(5.497, 1e-2)

        # BE/simplejk_A.m.hm.avg
        assert system_level_metrics['F']['rouge-be-hm_jk']['recall'] == pytest.approx(9.114, 1e-2)
        assert system_level_metrics['H']['rouge-be-hm_jk']['recall'] == pytest.approx(8.690, 1e-1)
        assert system_level_metrics['D']['rouge-be-hm_jk']['recall'] == pytest.approx(8.449, 1e-1)
        assert system_level_metrics['22']['rouge-be-hm_jk']['recall'] == pytest.approx(5.973, 1e-2)
        assert system_level_metrics['23']['rouge-be-hm_jk']['recall'] == pytest.approx(5.828, 1e-2)

        # aesop_allpeers_A
        assert system_level_metrics['A']['aesop']['1'] == pytest.approx(0.09517478261, 1e-2)
        assert system_level_metrics['C']['aesop']['8'] == pytest.approx(0.0, 1e-2)
        assert system_level_metrics['4']['aesop']['13'] == pytest.approx(0.6150630435, 1e-2)
        assert system_level_metrics['8']['aesop']['22'] == pytest.approx(0.3684913043, 1e-2)
        assert system_level_metrics['16']['aesop']['27'] == pytest.approx(11.80434783, 1e-2)

    @pytest.mark.skipif(not os.path.exists(_metrics_B_file_path), reason='TAC 2010-B metrics file does not exist')
    def test_system_level_B(self):
        summary_level_metrics = JsonlReader(_metrics_B_file_path, Metrics).read()
        system_level_metrics = aggregate_metrics(summary_level_metrics)

        # Check a few metrics to make sure they are equal to what's in the NIST files
        # ROUGE/rouge2_B.m.avg
        assert system_level_metrics['16']['rouge-2']['recall'] == pytest.approx(8.024, 1e-2)
        assert system_level_metrics['13']['rouge-2']['recall'] == pytest.approx(7.913, 1e-2)
        assert system_level_metrics['36']['rouge-2']['recall'] == pytest.approx(7.311, 1e-2)
        assert system_level_metrics['8']['rouge-2']['recall'] == pytest.approx(7.251, 1e-2)
        assert system_level_metrics['4']['rouge-2']['recall'] == pytest.approx(7.058, 1e-2)

        # ROUGE/rouge2_B.jk.m.avg
        assert system_level_metrics['D']['rouge-2_jk']['recall'] == pytest.approx(13.021, 1e-2)
        assert system_level_metrics['E']['rouge-2_jk']['recall'] == pytest.approx(10.196, 1e-1)
        assert system_level_metrics['F']['rouge-2_jk']['recall'] == pytest.approx(9.777, 1e-2)
        assert system_level_metrics['16']['rouge-2_jk']['recall'] == pytest.approx(7.993, 1e-2)
        assert system_level_metrics['13']['rouge-2_jk']['recall'] == pytest.approx(7.902, 1e-2)

        # ROUGE/rougeSU4_B.m.avg
        assert system_level_metrics['16']['rouge-su4']['recall'] == pytest.approx(12.006, 1e-2)
        assert system_level_metrics['13']['rouge-su4']['recall'] == pytest.approx(11.878, 1e-2)
        assert system_level_metrics['6']['rouge-su4']['recall'] == pytest.approx(11.198, 1e-2)
        assert system_level_metrics['22']['rouge-su4']['recall'] == pytest.approx(11.107, 1e-2)
        assert system_level_metrics['8']['rouge-su4']['recall'] == pytest.approx(11.039, 1e-2)

        # ROUGE/rougeSU4_B.jk.m.avg
        assert system_level_metrics['D']['rouge-su4_jk']['recall'] == pytest.approx(16.193, 1e-2)
        assert system_level_metrics['E']['rouge-su4_jk']['recall'] == pytest.approx(13.978, 1e-2)
        assert system_level_metrics['G']['rouge-su4_jk']['recall'] == pytest.approx(13.573, 1e-2)
        assert system_level_metrics['16']['rouge-su4_jk']['recall'] == pytest.approx(11.979, 1e-2)
        assert system_level_metrics['13']['rouge-su4_jk']['recall'] == pytest.approx(11.869, 1e-2)

        # manual/manual.model.B.avg
        assert system_level_metrics['A']['num_scus_jk'] == pytest.approx(6.609, 1e-2)
        assert system_level_metrics['B']['num_scus_jk'] == pytest.approx(7.696, 1e-2)
        assert system_level_metrics['C']['num_scus_jk'] == pytest.approx(5.913, 1e-2)

        assert system_level_metrics['A']['modified_pyramid_score_jk'] == pytest.approx(0.629, 1e-2)
        assert system_level_metrics['B']['modified_pyramid_score_jk'] == pytest.approx(0.729, 1e-2)
        assert system_level_metrics['C']['modified_pyramid_score_jk'] == pytest.approx(0.551, 1e-2)

        assert system_level_metrics['A']['linguistic_quality'] == pytest.approx(4.913, 1e-2)
        assert system_level_metrics['B']['linguistic_quality'] == pytest.approx(4.826, 1e-2)
        assert system_level_metrics['C']['linguistic_quality'] == pytest.approx(4.870, 1e-2)

        assert system_level_metrics['A']['overall_responsiveness'] == pytest.approx(4.783, 1e-2)
        assert system_level_metrics['B']['overall_responsiveness'] == pytest.approx(4.783, 1e-2)
        assert system_level_metrics['C']['overall_responsiveness'] == pytest.approx(4.826, 1e-2)

        # manual/manual.peer.B.avg
        assert system_level_metrics['1']['modified_pyramid_score'] == pytest.approx(0.187, 1e-2)
        assert system_level_metrics['2']['modified_pyramid_score'] == pytest.approx(0.262, 1e-2)
        assert system_level_metrics['3']['modified_pyramid_score'] == pytest.approx(0.235, 1e-2)

        assert system_level_metrics['1']['num_scus'] == pytest.approx(2.065, 1e-2)
        assert system_level_metrics['2']['num_scus'] == pytest.approx(2.804, 1e-2)
        assert system_level_metrics['3']['num_scus'] == pytest.approx(2.609, 1e-2)

        assert system_level_metrics['1']['num_repetitions'] == pytest.approx(0.348, 1e-2)
        assert system_level_metrics['2']['num_repetitions'] == pytest.approx(0.522, 1e-2)
        assert system_level_metrics['3']['num_repetitions'] == pytest.approx(0.348, 1e-2)

        assert system_level_metrics['1']['modified_pyramid_score_jk'] == pytest.approx(0.184, 1e-2)
        assert system_level_metrics['2']['modified_pyramid_score_jk'] == pytest.approx(0.256, 1e-2)
        assert system_level_metrics['3']['modified_pyramid_score_jk'] == pytest.approx(0.228, 1e-2)

        assert system_level_metrics['1']['linguistic_quality'] == pytest.approx(3.739, 1e-2)
        assert system_level_metrics['2']['linguistic_quality'] == pytest.approx(2.696, 1e-2)
        assert system_level_metrics['3']['linguistic_quality'] == pytest.approx(2.957, 1e-2)

        assert system_level_metrics['1']['overall_responsiveness'] == pytest.approx(2.022, 1e-2)
        assert system_level_metrics['2']['overall_responsiveness'] == pytest.approx(2.478, 1e-2)
        assert system_level_metrics['3']['overall_responsiveness'] == pytest.approx(2.217, 1e-2)

        # BE/simple_B.m.hm.avg
        assert system_level_metrics['16']['rouge-be-hm']['recall'] == pytest.approx(4.445, 1e-2)
        assert system_level_metrics['13']['rouge-be-hm']['recall'] == pytest.approx(4.417, 1e-2)
        assert system_level_metrics['8']['rouge-be-hm']['recall'] == pytest.approx(4.350, 1e-1)
        assert system_level_metrics['4']['rouge-be-hm']['recall'] == pytest.approx(4.115, 1e-2)
        assert system_level_metrics['22']['rouge-be-hm']['recall'] == pytest.approx(4.050, 1e-2)

        # BE/simplejk_B.m.hm.avg
        assert system_level_metrics['D']['rouge-be-hm_jk']['recall'] == pytest.approx(8.842, 1e-2)
        assert system_level_metrics['F']['rouge-be-hm_jk']['recall'] == pytest.approx(7.842, 1e-1)
        assert system_level_metrics['B']['rouge-be-hm_jk']['recall'] == pytest.approx(7.081, 1e-1)
        assert system_level_metrics['16']['rouge-be-hm_jk']['recall'] == pytest.approx(4.411, 1e-2)
        assert system_level_metrics['13']['rouge-be-hm_jk']['recall'] == pytest.approx(4.402, 1e-2)

        # aesop_allpeers_B
        assert system_level_metrics['B']['aesop']['2'] == pytest.approx(0.1358091304, 1e-2)
        assert system_level_metrics['E']['aesop']['4'] == pytest.approx(0.1376682609, 1e-2)
        assert system_level_metrics['6']['aesop']['7'] == pytest.approx(0.2641304348, 1e-2)
        assert system_level_metrics['9']['aesop']['20'] == pytest.approx(0.09438347826, 1e-2)
        assert system_level_metrics['14']['aesop']['22'] == pytest.approx(0.3394478261, 1e-2)
