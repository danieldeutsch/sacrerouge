import os
import pytest

from sacrerouge.common.testing.metric_test_cases import ReferenceBasedMetricTestCase
from sacrerouge.common.testing.util import sacrerouge_command_exists
from sacrerouge.metrics import APES


@pytest.mark.skipif('APES_ENV' not in os.environ, reason='PyrEval python environment environment variable not set')
class TestQAEval(ReferenceBasedMetricTestCase):
    def test_apes(self):
        # This is a regression test, not necessarily a test for correctness
        metric = APES(environment_name=os.environ['APES_ENV'], verbose=True)
        expected_output = [
            {'APES': {'accuracy': 10.256410256410257, 'num_correct': 4}},
            {'APES': {'accuracy': 30.448717948717952, 'num_correct': 10}},
            {'APES': {'accuracy': 21.634615384615387, 'num_correct': 5}},
            {'APES': {'accuracy': 23.076923076923077, 'num_correct': 6}},
            {'APES': {'accuracy': 36.11111111111111, 'num_correct': 14}},
            {'APES': {'accuracy': 24.074074074074076, 'num_correct': 10}},
            {'APES': {'accuracy': 34.72222222222222, 'num_correct': 10}},
            {'APES': {'accuracy': 36.111111111111114, 'num_correct': 10}},
            {'APES': {'accuracy': 35.90203106332139, 'num_correct': 28}},
            {'APES': {'accuracy': 40.47422111938241, 'num_correct': 31}},
            {'APES': {'accuracy': 41.308243727598565, 'num_correct': 22}},
            {'APES': {'accuracy': 32.81637717121588, 'num_correct': 19}}
        ]
        super().assert_expected_output(metric, expected_output)

    def test_apes_order_invariant(self):
        metric = APES(environment_name=os.environ['APES_ENV'])
        self.assert_order_invariant(metric)

    def test_command_exists(self):
        assert sacrerouge_command_exists(['apes'])

    def test_setup_command_exists(self):
        assert sacrerouge_command_exists(['setup-metric', 'apes'])