import os
import pytest

from sacrerouge.common.testing.metric_test_cases import ReferenceBasedMetricTestCase
from sacrerouge.metrics import S3


@pytest.mark.skipif('S3_ENV' not in os.environ, reason='S3 python environment environment variable not set')
class TestS3(ReferenceBasedMetricTestCase):
    def test_s3(self):
        # This is a regression test, not necessarily a test for correctness
        metric = S3(environment_name=os.environ['S3_ENV'])
        expected_output = [
            {'s3': {'pyr': 0.32191771068281394, 'resp': 0.43112947213398156}},
            {'s3': {'pyr': 0.49038453876892796, 'resp': 0.5689795160671101}},
            {'s3': {'pyr': 0.47786455220076274, 'resp': 0.548172710896836}},
            {'s3': {'pyr': 0.3803879523604371, 'resp': 0.46652343758025827}},
            {'s3': {'pyr': 0.35703890425311635, 'resp': 0.43948176094166214}},
            {'s3': {'pyr': 0.39784433258660734, 'resp': 0.48528832257788146}},
            {'s3': {'pyr': 0.5483975017522531, 'resp': 0.6088455902978009}},
            {'s3': {'pyr': 0.5510649124151888, 'resp': 0.6052093249379357}},
            {'s3': {'pyr': 0.3891717207498385, 'resp': 0.48441896558584596}},
            {'s3': {'pyr': 0.5833618133817302, 'resp': 0.6298526245098648}},
            {'s3': {'pyr': 0.5346016112603917, 'resp': 0.593030815989284}},
            {'s3': {'pyr': 0.46100829186334746, 'resp': 0.5209557553762801}}
        ]
        super().assert_expected_output(metric, expected_output)

    def test_s3_order_invariant(self):
        metric = S3(environment_name=os.environ['S3_ENV'])
        self.assert_order_invariant(metric)

    def test_commandline_runs(self):
        self.assert_commandline_runs('s3', ['--environment_name', f'{os.environ["S3_ENV"]}'])