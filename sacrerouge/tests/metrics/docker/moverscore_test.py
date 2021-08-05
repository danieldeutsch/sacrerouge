import pytest
from repro.common.docker import image_exists

from sacrerouge.common.testing.metric_test_cases import ReferenceBasedMetricTestCase
from sacrerouge.common.testing.util import sacrerouge_command_exists
from sacrerouge.metrics.docker import DockerMoverScore


@pytest.mark.skipif(not image_exists("zhao2019"), reason="Docker image \"zhao2019\" does not exist")
class TestDockerMoverScore(ReferenceBasedMetricTestCase):
    def test_docker_moverscore(self):
        # This is a regression test, not necessarily a test for correctness
        metric = DockerMoverScore()
        expected_output = [
            {"moverscore": 0.5363679808125064},
            {"moverscore": 0.553204695560149},
            {"moverscore": 0.5594086145883774},
            {"moverscore": 0.5478360937605564},
            {"moverscore": 0.540025446393662},
            {"moverscore": 0.5400406779008134},
            {"moverscore": 0.5630475426798369},
            {"moverscore": 0.5661348139567364},
            {"moverscore": 0.5565022067471124},
            {"moverscore": 0.5688220284325299},
            {"moverscore": 0.5642806008389394},
            {"moverscore": 0.5521844453777212}
        ]
        super().assert_expected_output(metric, expected_output)

    def test_docker_moverscore_order_invariant(self):
        metric = DockerMoverScore()
        self.assert_order_invariant(metric)

    def test_command_exists(self):
        assert sacrerouge_command_exists(['docker-moverscore'])
