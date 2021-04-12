import os
import pytest

from sacrerouge.common.testing.metric_test_cases import ReferenceBasedMetricTestCase
from sacrerouge.common.testing.util import sacrerouge_command_exists
from sacrerouge.metrics import PyrEval


@pytest.mark.skipif('PYREVAL_ENV' not in os.environ, reason='PyrEval python environment environment variable not set')
class TestPyrEval(ReferenceBasedMetricTestCase):
    def test_pyreval(self):
        # This is a regression test, not necessarily a test for correctness
        metric = PyrEval(environment_name=os.environ['PYREVAL_ENV'])
        expected_output = [
            {'pyreval': {'raw': 12, 'quality': 0.375, 'coverage': 0.2553191489361702, 'comprehensive': 0.31515957446808507}},
            {'pyreval': {'raw': 16, 'quality': 0.47058823529411764, 'coverage': 0.3404255319148936, 'comprehensive': 0.4055068836045056}},
            {'pyreval': {'raw': 12, 'quality': 0.631578947368421, 'coverage': 0.6666666666666666, 'comprehensive': 0.6491228070175439}},
            {'pyreval': {'raw': 8, 'quality': 0.2857142857142857, 'coverage': 0.5, 'comprehensive': 0.39285714285714285}},
            {'pyreval': {'raw': 17, 'quality': 0.4857142857142857, 'coverage': 0.5, 'comprehensive': 0.4928571428571429}},
            {'pyreval': {'raw': 17, 'quality': 0.4857142857142857, 'coverage': 0.5, 'comprehensive': 0.4928571428571429}},
            {'pyreval': {'raw': 11, 'quality': 0.5789473684210527, 'coverage': 0.7857142857142857, 'comprehensive': 0.6823308270676691}},
            {'pyreval': {'raw': 11, 'quality': 0.7857142857142857, 'coverage': 0.7333333333333333, 'comprehensive': 0.7595238095238095}},
            {'pyreval': {'raw': 9, 'quality': 0.2903225806451613, 'coverage': 0.2571428571428571, 'comprehensive': 0.2737327188940092}},
            {'pyreval': {'raw': 19, 'quality': 0.5277777777777778, 'coverage': 0.5428571428571428, 'comprehensive': 0.5353174603174603}},
            {'pyreval': {'raw': 10, 'quality': 0.625, 'coverage': 0.625, 'comprehensive': 0.625}},
            {'pyreval': {'raw': 8, 'quality': 0.4, 'coverage': 0.5333333333333333, 'comprehensive': 0.4666666666666667}}
        ]
        super().assert_expected_output(metric, expected_output)

    def test_pyreval_order_invariant(self):
        metric = PyrEval(environment_name=os.environ['PYREVAL_ENV'])
        self.assert_order_invariant(metric)

    def test_single_reference(self):
        metric = PyrEval(environment_name=os.environ['PYREVAL_ENV'])
        with self.assertRaises(Exception):
            metric.score('The summary', ['The single reference summary'])

    def test_command_exists(self):
        assert sacrerouge_command_exists(['pyreval'])

    def test_setup_command_exists(self):
        assert sacrerouge_command_exists(['setup-metric', 'pyreval'])