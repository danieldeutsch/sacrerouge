import pytest
from repro.common.docker import image_exists
from repro.models.yuan2021 import DEFAULT_IMAGE

from sacrerouge.common.testing.metric_test_cases import ReferenceBasedMetricTestCase
from sacrerouge.common.testing.util import sacrerouge_command_exists, get_gpu_device
from sacrerouge.metrics.docker import DockerBARTScore


@pytest.mark.skipif(not image_exists(DEFAULT_IMAGE), reason=f"Docker image \"{DEFAULT_IMAGE}\" does not exist")
class TestDockerBARTScore(ReferenceBasedMetricTestCase):
    def test_docker_bartscore(self):
        # This is a regression test, not necessarily a test for correctness
        metric = DockerBARTScore(device=get_gpu_device())
        expected_output = [
            {"bartscore": -6.032016754150391},
            {"bartscore": -5.175032536188762},
            {"bartscore": -4.962132930755615},
            {"bartscore": -5.526906728744507},
            {"bartscore": -6.743911584218343},
            {"bartscore": -5.51335604985555},
            {"bartscore": -5.157900094985962},
            {"bartscore": -4.771411180496216},
            {"bartscore": -8.69148333867391},
            {"bartscore": -4.837590217590332},
            {"bartscore": -4.934406042098999},
            {"bartscore": -5.645484447479248}
        ]
        super().assert_expected_output(metric, expected_output)

    def test_docker_bertscore_order_invariant(self):
        metric = DockerBARTScore(device=get_gpu_device())
        self.assert_order_invariant(metric)

    def test_command_exists(self):
        assert sacrerouge_command_exists(['docker-bartscore'])
