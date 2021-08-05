import os
import pytest
from repro.common.docker import image_exists

from sacrerouge.common.testing.metric_test_cases import ReferenceBasedMetricTestCase
from sacrerouge.common.testing.util import sacrerouge_command_exists
from sacrerouge.metrics.docker import DockerBluert


@pytest.mark.skipif(not image_exists("sellam2020"), reason="Docker image \"sellam2020\" does not exist")
class TestDockerBleurt(ReferenceBasedMetricTestCase):
    def test_docker_bleurt(self):
        # This is a regression test, not necessarily a test for correctness
        metric = DockerBluert()
        expected_output = [
            {'bleurt': {'mean': -1.0048247178395588, 'max': -0.9933006763458252}},
            {'bleurt': {'mean': -1.0668554306030273, 'max': -1.0025169849395752}},
            {'bleurt': {'mean': -0.7564655840396881, 'max': -0.5489686727523804}},
            {'bleurt': {'mean': -0.6693709492683411, 'max': -0.39580726623535156}},
            {'bleurt': {'mean': -0.6533156832059225, 'max': -0.5730574727058411}},
            {'bleurt': {'mean': -0.4237842659155528, 'max': -0.25567689538002014}},
            {'bleurt': {'mean': -0.6848879158496857, 'max': -0.6829712390899658}},
            {'bleurt': {'mean': -0.5012103617191315, 'max': -0.30445921421051025}},
            {'bleurt': {'mean': -0.6940024892489115, 'max': -0.6559309959411621}},
            {'bleurt': {'mean': -0.6693291465441386, 'max': -0.6304700374603271}},
            {'bleurt': {'mean': -0.8384850323200226, 'max': -0.7783546447753906}},
            {'bleurt': {'mean': -0.5458722561597824, 'max': -0.37889066338539124}}
        ]
        super().assert_expected_output(metric, expected_output)

    def test_bleurt_order_invariant(self):
        metric = DockerBluert()
        self.assert_order_invariant(metric)

    def test_command_exists(self):
        assert sacrerouge_command_exists(['docker-bleurt'])