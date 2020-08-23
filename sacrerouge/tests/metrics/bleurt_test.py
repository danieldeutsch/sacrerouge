import os
import pytest

from sacrerouge.common.testing.metric_test_cases import ReferenceBasedMetricTestCase
from sacrerouge.metrics import Bleurt


@pytest.mark.skipif('BLEURT_ENV' not in os.environ, reason='BLEURT python environment environment variable not set')
class TestBleurt(ReferenceBasedMetricTestCase):
    def test_bleurt(self):
        # This is a regression test, not necessarily a test for correctness
        metric = Bleurt(environment_name=os.environ['BLEURT_ENV'])
        expected_output = [
            {'bleurt': {'average': -1.0048247178395588, 'max': -0.9933006763458252}},
            {'bleurt': {'average': -1.0668554306030273, 'max': -1.0025169849395752}},
            {'bleurt': {'average': -0.7564655840396881, 'max': -0.5489686727523804}},
            {'bleurt': {'average': -0.6693709492683411, 'max': -0.39580726623535156}},
            {'bleurt': {'average': -0.6533156832059225, 'max': -0.5730574727058411}},
            {'bleurt': {'average': -0.4237842659155528, 'max': -0.25567689538002014}},
            {'bleurt': {'average': -0.6848879158496857, 'max': -0.6829712390899658}},
            {'bleurt': {'average': -0.5012103617191315, 'max': -0.30445921421051025}},
            {'bleurt': {'average': -0.6940024892489115, 'max': -0.6559309959411621}},
            {'bleurt': {'average': -0.6693291465441386, 'max': -0.6304700374603271}},
            {'bleurt': {'average': -0.8384850323200226, 'max': -0.7783546447753906}},
            {'bleurt': {'average': -0.5458722561597824, 'max': -0.37889066338539124}}
        ]
        super().assert_expected_output(metric, expected_output)

    def test_bleurt_order_invariant(self):
        metric = Bleurt(environment_name=os.environ['BLEURT_ENV'])
        self.assert_order_invariant(metric)