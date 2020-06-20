import os
import pytest
import unittest

from sacrerouge.commands.correlate import aggregate_metrics
from sacrerouge.data import Metrics
from sacrerouge.io import JsonlReader

_metrics_A_file_path = 'datasets/duc-tac/tac2011/v1.0/task1.A.metrics.jsonl'
_metrics_B_file_path = 'datasets/duc-tac/tac2011/v1.0/task1.B.metrics.jsonl'


class TestTAC2011SystemLevel(unittest.TestCase):
    @pytest.mark.skipif(not os.path.exists(_metrics_A_file_path), reason='TAC 2011-A metrics file does not exist')
    def test_system_level_A(self):
        summary_level_metrics = JsonlReader(_metrics_A_file_path, Metrics).read()
        system_level_metrics = aggregate_metrics(summary_level_metrics)

        # Check a few metrics to make sure they are equal to what's in the NIST files
        # ROUGE/rouge2_A.m.avg
        assert system_level_metrics['43']['rouge-2']['recall'] == pytest.approx(13.440, 1e-2)
        assert system_level_metrics['17']['rouge-2']['recall'] == pytest.approx(12.994, 1e-2)
        assert system_level_metrics['25']['rouge-2']['recall'] == pytest.approx(12.821, 1e-2)

        # ROUGE/rouge2_A.jk.m.avg
        assert system_level_metrics['D']['rouge-2_jk']['recall'] == pytest.approx(12.820, 1e-2)
        assert system_level_metrics['43']['rouge-2_jk']['recall'] == pytest.approx(13.447, 1e-2)
        assert system_level_metrics['17']['rouge-2_jk']['recall'] == pytest.approx(12.993, 1e-2)

        # ROUGE/rougeSU4_A.m.avg
        assert system_level_metrics['43']['rouge-su4']['recall'] == pytest.approx(16.519, 1e-2)
        assert system_level_metrics['17']['rouge-su4']['recall'] == pytest.approx(15.984, 1e-2)
        assert system_level_metrics['24']['rouge-su4']['recall'] == pytest.approx(15.975, 1e-2)

        # ROUGE/rougeSU4_A.jk.m.avg
        assert system_level_metrics['D']['rouge-su4_jk']['recall'] == pytest.approx(16.412, 1e-2)
        assert system_level_metrics['A']['rouge-su4_jk']['recall'] == pytest.approx(16.118, 1e-2)
        assert system_level_metrics['43']['rouge-su4_jk']['recall'] == pytest.approx(16.519, 1e-2)

        # manual/manual.model.A.avg
        assert system_level_metrics['A']['num_scus_jk'] == pytest.approx(10.227, 1e-2)
        assert system_level_metrics['B']['num_scus_jk'] == pytest.approx(9.773, 1e-2)
        assert system_level_metrics['C']['num_scus_jk'] == pytest.approx(9.818, 1e-2)

        assert system_level_metrics['A']['modified_pyramid_score_jk'] == pytest.approx(0.771, 1e-2)
        assert system_level_metrics['B']['modified_pyramid_score_jk'] == pytest.approx(0.781, 1e-2)
        assert system_level_metrics['C']['modified_pyramid_score_jk'] == pytest.approx(0.752, 1e-2)

        assert system_level_metrics['A']['linguistic_quality'] == pytest.approx(4.864, 1e-2)
        assert system_level_metrics['B']['linguistic_quality'] == pytest.approx(4.818, 1e-2)
        assert system_level_metrics['C']['linguistic_quality'] == pytest.approx(5.000, 1e-2)

        assert system_level_metrics['A']['overall_responsiveness'] == pytest.approx(4.818, 1e-2)
        assert system_level_metrics['B']['overall_responsiveness'] == pytest.approx(4.727, 1e-2)
        assert system_level_metrics['C']['overall_responsiveness'] == pytest.approx(4.955, 1e-2)

        # manual/manual.peer.A.avg
        assert system_level_metrics['1']['modified_pyramid_score'] == pytest.approx(0.304, 1e-2)
        assert system_level_metrics['2']['modified_pyramid_score'] == pytest.approx(0.362, 1e-2)
        assert system_level_metrics['3']['modified_pyramid_score'] == pytest.approx(0.439, 1e-2)

        assert system_level_metrics['1']['num_scus'] == pytest.approx(3.909, 1e-2)
        assert system_level_metrics['2']['num_scus'] == pytest.approx(4.614, 1e-2)
        assert system_level_metrics['3']['num_scus'] == pytest.approx(5.750, 1e-2)

        assert system_level_metrics['1']['num_repetitions'] == pytest.approx(0.455, 1e-2)
        assert system_level_metrics['2']['num_repetitions'] == pytest.approx(1.432, 1e-2)
        assert system_level_metrics['3']['num_repetitions'] == pytest.approx(1.409, 1e-2)

        assert system_level_metrics['1']['modified_pyramid_score_jk'] == pytest.approx(0.300, 1e-2)
        assert system_level_metrics['2']['modified_pyramid_score_jk'] == pytest.approx(0.358, 1e-2)
        assert system_level_metrics['3']['modified_pyramid_score_jk'] == pytest.approx(0.433, 1e-2)

        assert system_level_metrics['1']['linguistic_quality'] == pytest.approx(3.205, 1e-2)
        assert system_level_metrics['2']['linguistic_quality'] == pytest.approx(2.818, 1e-2)
        assert system_level_metrics['3']['linguistic_quality'] == pytest.approx(2.705, 1e-2)

        assert system_level_metrics['1']['overall_responsiveness'] == pytest.approx(2.500, 1e-2)
        assert system_level_metrics['2']['overall_responsiveness'] == pytest.approx(2.841, 1e-2)
        assert system_level_metrics['3']['overall_responsiveness'] == pytest.approx(3.045, 1e-2)

        # BE/simple_A.m.hm.avg
        assert system_level_metrics['43']['rouge-be-hm']['recall'] == pytest.approx(8.565, 1e-2)
        assert system_level_metrics['17']['rouge-be-hm']['recall'] == pytest.approx(8.153, 1e-2)
        assert system_level_metrics['25']['rouge-be-hm']['recall'] == pytest.approx(8.012, 1e-2)

        # BE/simplejk_A.m.hm.avg
        assert system_level_metrics['D']['rouge-be-hm_jk']['recall'] == pytest.approx(9.085, 1e-2)
        assert system_level_metrics['E']['rouge-be-hm_jk']['recall'] == pytest.approx(8.628, 1e-2)
        assert system_level_metrics['43']['rouge-be-hm_jk']['recall'] == pytest.approx(8.553, 1e-2)

        # aesop_allpeers_A
        assert system_level_metrics['A']['aesop']['1'] == pytest.approx(0.1191786364, 1e-2)
        assert system_level_metrics['C']['aesop']['8'] == pytest.approx(3.853212409, 1e-2)
        assert system_level_metrics['4']['aesop']['13'] == pytest.approx(0.4008335416, 1e-2)

    @pytest.mark.skipif(not os.path.exists(_metrics_B_file_path), reason='TAC 2011-B metrics file does not exist')
    def test_system_level_B(self):
        summary_level_metrics = JsonlReader(_metrics_B_file_path, Metrics).read()
        system_level_metrics = aggregate_metrics(summary_level_metrics)

        # Check a few metrics to make sure they are equal to what's in the NIST files
        # ROUGE/rouge2_B.m.avg
        assert system_level_metrics['43']['rouge-2']['recall'] == pytest.approx(9.581, 1e-2)
        assert system_level_metrics['25']['rouge-2']['recall'] == pytest.approx(9.259, 1e-2)
        assert system_level_metrics['17']['rouge-2']['recall'] == pytest.approx(8.855, 1e-2)

        # ROUGE/rouge2_B.jk.m.avg
        assert system_level_metrics['E']['rouge-2_jk']['recall'] == pytest.approx(11.474, 1e-2)
        assert system_level_metrics['H']['rouge-2_jk']['recall'] == pytest.approx(10.865, 1e-1)
        assert system_level_metrics['43']['rouge-2_jk']['recall'] == pytest.approx(9.589, 1e-2)

        # ROUGE/rougeSU4_B.m.avg
        assert system_level_metrics['43']['rouge-su4']['recall'] == pytest.approx(13.080, 1e-2)
        assert system_level_metrics['24']['rouge-su4']['recall'] == pytest.approx(12.803, 1e-2)
        assert system_level_metrics['17']['rouge-su4']['recall'] == pytest.approx(12.792, 1e-2)

        # ROUGE/rougeSU4_B.jk.m.avg
        assert system_level_metrics['E']['rouge-su4_jk']['recall'] == pytest.approx(14.941, 1e-2)
        assert system_level_metrics['D']['rouge-su4_jk']['recall'] == pytest.approx(14.368, 1e-2)
        assert system_level_metrics['43']['rouge-su4_jk']['recall'] == pytest.approx(13.086, 1e-2)

        # manual/manual.model.B.avg
        assert system_level_metrics['A']['num_scus_jk'] == pytest.approx(6.682, 1e-2)
        assert system_level_metrics['B']['num_scus_jk'] == pytest.approx(5.409, 1e-2)
        assert system_level_metrics['C']['num_scus_jk'] == pytest.approx(5.864, 1e-2)

        assert system_level_metrics['A']['modified_pyramid_score_jk'] == pytest.approx(0.663, 1e-2)
        assert system_level_metrics['B']['modified_pyramid_score_jk'] == pytest.approx(0.554, 1e-2)
        assert system_level_metrics['C']['modified_pyramid_score_jk'] == pytest.approx(0.565, 1e-2)

        assert system_level_metrics['A']['linguistic_quality'] == pytest.approx(4.909, 1e-2)
        assert system_level_metrics['B']['linguistic_quality'] == pytest.approx(4.909, 1e-2)
        assert system_level_metrics['C']['linguistic_quality'] == pytest.approx(4.955, 1e-2)

        assert system_level_metrics['A']['overall_responsiveness'] == pytest.approx(4.773, 1e-2)
        assert system_level_metrics['B']['overall_responsiveness'] == pytest.approx(4.500, 1e-2)
        assert system_level_metrics['C']['overall_responsiveness'] == pytest.approx(4.682, 1e-2)

        # manual/manual.peer.B.avg
        assert system_level_metrics['1']['modified_pyramid_score'] == pytest.approx(0.237, 1e-2)
        assert system_level_metrics['2']['modified_pyramid_score'] == pytest.approx(0.284, 1e-2)
        assert system_level_metrics['3']['modified_pyramid_score'] == pytest.approx(0.327, 1e-2)

        assert system_level_metrics['1']['num_scus'] == pytest.approx(2.636, 1e-2)
        assert system_level_metrics['2']['num_scus'] == pytest.approx(3.136, 1e-2)
        assert system_level_metrics['3']['num_scus'] == pytest.approx(3.682, 1e-2)

        assert system_level_metrics['1']['num_repetitions'] == pytest.approx(0.364, 1e-2)
        assert system_level_metrics['2']['num_repetitions'] == pytest.approx(0.568, 1e-2)
        assert system_level_metrics['3']['num_repetitions'] == pytest.approx(0.727, 1e-2)

        assert system_level_metrics['1']['modified_pyramid_score_jk'] == pytest.approx(0.234, 1e-2)
        assert system_level_metrics['2']['modified_pyramid_score_jk'] == pytest.approx(0.280, 1e-2)
        assert system_level_metrics['3']['modified_pyramid_score_jk'] == pytest.approx(0.322, 1e-2)

        assert system_level_metrics['1']['linguistic_quality'] == pytest.approx(3.455, 1e-2)
        assert system_level_metrics['2']['linguistic_quality'] == pytest.approx(2.841, 1e-2)
        assert system_level_metrics['3']['linguistic_quality'] == pytest.approx(2.886, 1e-2)

        assert system_level_metrics['1']['overall_responsiveness'] == pytest.approx(2.091, 1e-2)
        assert system_level_metrics['2']['overall_responsiveness'] == pytest.approx(2.114, 1e-2)
        assert system_level_metrics['3']['overall_responsiveness'] == pytest.approx(2.500, 1e-2)

        # BE/simple_B.m.hm.avg
        assert system_level_metrics['43']['rouge-be-hm']['recall'] == pytest.approx(6.473, 1e-2)
        assert system_level_metrics['25']['rouge-be-hm']['recall'] == pytest.approx(5.937, 1e-2)
        assert system_level_metrics['26']['rouge-be-hm']['recall'] == pytest.approx(5.717, 1e-1)

        # BE/simplejk_B.m.hm.avg
        assert system_level_metrics['E']['rouge-be-hm_jk']['recall'] == pytest.approx(7.970, 1e-2)
        assert system_level_metrics['D']['rouge-be-hm_jk']['recall'] == pytest.approx(7.341, 1e-1)
        assert system_level_metrics['43']['rouge-be-hm_jk']['recall'] == pytest.approx(6.480, 1e-1)

        # aesop_allpeers_B
        assert system_level_metrics['B']['aesop']['2'] == pytest.approx(0.1278890909, 1e-2)
        assert system_level_metrics['E']['aesop']['4'] == pytest.approx(0.4831818182, 1e-2)
        assert system_level_metrics['6']['aesop']['8'] == pytest.approx(1.003988068, 1e-2)
