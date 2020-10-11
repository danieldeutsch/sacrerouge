import json
import os
import pytest

from sacrerouge.common.testing import FIXTURES_ROOT
from sacrerouge.common.testing.metric_test_cases import DocumentBasedMetricTestCase
from sacrerouge.metrics import SUPERT

_TOPIC_1 = f'{FIXTURES_ROOT}/data/supert/topic_1.json'


@pytest.mark.skipif('SUPERT_ENV' not in os.environ, reason='SUPERT python environment environment variable not set')
class TestSUPERT(DocumentBasedMetricTestCase):
    def test_example(self):
        # Tests to make sure we get the same output as running the example in the original repository
        topic1 = json.load(open(_TOPIC_1, 'r'))
        documents = topic1['documents']
        summaries = topic1['summaries']

        supert = SUPERT(os.environ['SUPERT_ENV'])
        expected_output = [
            {'supert': 0.4724942240404387},
            {'supert': 0.38462300158000995},
            {'supert': 0.4947284743279349},
            {'supert': 0.501369657633312},
            {'supert': 0.5108337561530968}
        ]
        actual_output = supert.score_multi(summaries, documents)

        for expected, actual in zip(expected_output, actual_output):
            assert expected == pytest.approx(actual, 1e-4)

    def test_supert(self):
        # This is a regression test, not necessarily a test for correctness
        metric = SUPERT(os.environ['SUPERT_ENV'])
        expected_output = [
            {'supert': 0.46000519191903655},
            {'supert': 0.4766808595557026},
            {'supert': 0.4467075912019479},
            {'supert': 0.4049276967180207},
            {'supert': 0.4518371118994575},
            {'supert': 0.4672364921295776},
            {'supert': 0.4413289374922482},
            {'supert': 0.41049172025776465},
            {'supert': 0.5598548871327522},
            {'supert': 0.5688464141370209},
            {'supert': 0.5096871293947829},
            {'supert': 0.4635047957553205}
        ]
        super().assert_expected_output(metric, expected_output)

    def test_supert_order_invariant(self):
        metric = SUPERT(os.environ['SUPERT_ENV'])
        self.assert_order_invariant(metric)