import pytest
from repro.common.docker import image_exists
from repro.models.zhang2021 import DEFAULT_IMAGE

from sacrerouge.common.testing.metric_test_cases import ReferenceBasedMetricTestCase
from sacrerouge.common.testing.util import sacrerouge_command_exists, get_gpu_device
from sacrerouge.metrics.docker import DockerLite3Pyramid


@pytest.mark.skipif(not image_exists(DEFAULT_IMAGE), reason=f"Docker image \"{DEFAULT_IMAGE}\" does not exist")
class TestDockerLite3Pyramid(ReferenceBasedMetricTestCase):
    def test_docker_bartscore(self):
        # This is a regression test, not necessarily a test for correctness
        metric = DockerLite3Pyramid(device=get_gpu_device())
        expected_output = [
            {
                "p2c": 0.08140615014485485,
                "l2c": 0.05044091710758377,
                "p3c": 0.059472563714043525,
                "l3c": 0.02857142857142857
            },
            {
                "p2c": 0.08951288953586624,
                "l2c": 0.06948853615520283,
                "p3c": 0.06532527711269559,
                "l3c": 0.05044091710758377
            },
            {
                "p2c": 0.17433017155394895,
                "l2c": 0.17017017017017017,
                "p3c": 0.13583989035971747,
                "l3c": 0.1111111111111111
            },
            {
                "p2c": 0.1265341025041306,
                "l2c": 0.07142857142857142,
                "p3c": 0.09825152735604317,
                "l3c": 0.05714285714285714
            },
            {
                "p2c": 0.0456428095766449,
                "l2c": 0.013333333333333334,
                "p3c": 0.02957398398254298,
                "l3c": 0.013333333333333334
            },
            {
                "p2c": 0.058193410683831104,
                "l2c": 0.013333333333333334,
                "p3c": 0.04073674187626284,
                "l3c": 0.013333333333333334
            },
            {
                "p2c": 0.2958913596694061,
                "l2c": 0.2967741935483871,
                "p3c": 0.24035046127238952,
                "l3c": 0.27677419354838706
            },
            {
                "p2c": 0.25973563567713304,
                "l2c": 0.2335928809788654,
                "p3c": 0.20736325674332448,
                "l3c": 0.2335928809788654
            },
            {
                "p2c": 0.18896490568749458,
                "l2c": 0.17481203007518795,
                "p3c": 0.16216605451319907,
                "l3c": 0.17481203007518795
            },
            {
                "p2c": 0.2612303528395576,
                "l2c": 0.2606516290726817,
                "p3c": 0.21209689358491365,
                "l3c": 0.23402255639097747
            },
            {
                "p2c": 0.2605075205306223,
                "l2c": 0.262406015037594,
                "p3c": 0.20608325105629471,
                "l3c": 0.20751879699248119
            },
            {
                "p2c": 0.1430279545373196,
                "l2c": 0.15535714285714286,
                "p3c": 0.10879598084325803,
                "l3c": 0.1285714285714286
            }
        ]
        super().assert_expected_output(metric, expected_output)

    def test_docker_lite3pyramid_order_invariant(self):
        metric = DockerLite3Pyramid(device=get_gpu_device())
        self.assert_order_invariant(metric, abs=1e-4)

    def test_command_exists(self):
        assert sacrerouge_command_exists(['docker-lite3pyramid'])
