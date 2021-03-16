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
            {'APES': 10.256410256410257},
            {'APES': 30.448717948717952},
            {'APES': 27.884615384615387},
            {'APES': 26.923076923076923},
            {'APES': 27.777777777777782},
            {'APES': 24.074074074074076},
            {'APES': 34.72222222222222},
            {'APES': 36.111111111111114},
            {'APES': 38.05256869772999},
            {'APES': 38.62236926753056},
            {'APES': 39.69534050179212},
            {'APES': 26.054590570719604}
        ]
        super().assert_expected_output(metric, expected_output)

    def test_apes_order_invariant(self):
        metric = APES(environment_name=os.environ['APES_ENV'])
        self.assert_order_invariant(metric)

    def test_command_exists(self):
        assert sacrerouge_command_exists(['apes'])

    def test_setup_command_exists(self):
        assert sacrerouge_command_exists(['setup-metric', 'apes'])