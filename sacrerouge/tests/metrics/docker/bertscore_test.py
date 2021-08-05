import pytest
from repro.common.docker import image_exists

from sacrerouge.common.testing.metric_test_cases import ReferenceBasedMetricTestCase
from sacrerouge.common.testing.util import sacrerouge_command_exists
from sacrerouge.metrics.docker import DockerBertScore


@pytest.mark.skipif(not image_exists("zhang2020"), reason="Docker image \"zhang2020\" does not exist")
class TestDockerBertScore(ReferenceBasedMetricTestCase):
    def test_docker_bertscore(self):
        # This is a regression test, not necessarily a test for correctness
        metric = DockerBertScore()
        expected_output = [
            {'bertscore': {'precision': 0.8534530401229858, 'recall': 0.8503388166427612, 'f1': 0.8518930673599243}},
            {'bertscore': {'precision': 0.8642909526824951, 'recall': 0.8720692992210388, 'f1': 0.8681626319885254}},
            {'bertscore': {'precision': 0.8623127341270447, 'recall': 0.8670819997787476, 'f1': 0.8646908402442932}},
            {'bertscore': {'precision': 0.8549671173095703, 'recall': 0.856684148311615, 'f1': 0.8558247685432434}},
            {'bertscore': {'precision': 0.8397505283355713, 'recall': 0.8507593870162964, 'f1': 0.8451763987541199}},
            {'bertscore': {'precision': 0.8410190343856812, 'recall': 0.8510528206825256, 'f1': 0.8460061550140381}},
            {'bertscore': {'precision': 0.8653707504272461, 'recall': 0.8665218949317932, 'f1': 0.8659459948539734}},
            {'bertscore': {'precision': 0.868201494216919, 'recall': 0.8704793453216553, 'f1': 0.8693389296531677}},
            {'bertscore': {'precision': 0.9007625579833984, 'recall': 0.8653964400291443, 'f1': 0.8827253580093384}},
            {'bertscore': {'precision': 0.8833473920822144, 'recall': 0.8772095441818237, 'f1': 0.8802677989006042}},
            {'bertscore': {'precision': 0.8683465719223022, 'recall': 0.8797310590744019, 'f1': 0.8740017414093018}},
            {'bertscore': {'precision': 0.8667279481887817, 'recall': 0.8681085109710693, 'f1': 0.8665944337844849}}
        ]
        super().assert_expected_output(metric, expected_output)

    def test_docker_bertscore_order_invariant(self):
        metric = DockerBertScore()
        self.assert_order_invariant(metric)

    def test_command_exists(self):
        assert sacrerouge_command_exists(['docker-bertscore'])
