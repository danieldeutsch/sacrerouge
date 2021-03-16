import os
import pytest

from sacrerouge.common.testing.metric_test_cases import ReferenceBasedMetricTestCase
from sacrerouge.common.testing.util import sacrerouge_command_exists
from sacrerouge.metrics import APES


@pytest.mark.skipif('APES_ENV' not in os.environ, reason='PyrEval python environment environment variable not set')
class TestQAEval(ReferenceBasedMetricTestCase):
    def test_apes(self):
        # This is a regression test, not necessarily a test for correctness
        metric = APES(environment_name=os.environ['APES_ENV'])
        expected_output = [
            {'APES': 10.256410256403332},
            {'APES': 30.448717948703335},
            {'APES': 21.6346153846},
            {'APES': 23.0769230769},
            {'APES': 34.25925925923334},
            {'APES': 24.074074074066668},
            {'APES': 30.55555555555},
            {'APES': 33.3333333333},
            {'APES': 36.108813528166667},
            {'APES': 40.979689366800004},
            {'APES': 41.3082437276},
            {'APES': 27.6674937965}
        ]
        super().assert_expected_output(metric, expected_output)

    def test_apes_order_invariant(self):
        metric = APES(environment_name=os.environ['APES_ENV'])
        self.assert_order_invariant(metric)

    def test_command_exists(self):
        assert sacrerouge_command_exists(['apes'])

    def test_setup_command_exists(self):
        assert sacrerouge_command_exists(['setup-metric', 'apes'])