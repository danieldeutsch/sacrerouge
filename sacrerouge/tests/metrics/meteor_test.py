import pytest

from sacrerouge.common.testing import FIXTURES_ROOT
from sacrerouge.common.testing.metric_test_cases import ReferenceBasedMetricTestCase
from sacrerouge.io import JsonlReader
from sacrerouge.metrics import Meteor


class TestMeteor(ReferenceBasedMetricTestCase):
        def test_meteor(self):
            # This is a regression test, not necessarily a test for correctness
            metric = Meteor()
            expected_output = [
                {'METEOR': 0.1669124164573825},
                {'METEOR': 0.1948832291162732},
                {'METEOR': 0.20611797558912198},
                {'METEOR': 0.16514495147439157},
                {'METEOR': 0.17681198359839032},
                {'METEOR': 0.1711431947904745},
                {'METEOR': 0.21743329361081287},
                {'METEOR': 0.21450528119487908},
                {'METEOR': 0.16550404185166837},
                {'METEOR': 0.21164463762707278},
                {'METEOR': 0.20412130512572657},
                {'METEOR': 0.18243523574488876}
            ]
            super().assert_expected_output(metric, expected_output)

        def test_bewte_order_invariant(self):
            metric = Meteor()
            self.assert_order_invariant(metric)

        def test_chen2018(self):
            """
            Tests to ensure that Meteor returns the expected score on the
            Chen 2018 data subset. I ran Meteor on the full data (~11k examples)
            which takes too long to run for a unit test. After confirming the numbers
            are the same as what is reported in the paper, I ran the code on just
            the subset, and this test ensures those numbers are returned.
            """
            gold_file_path = f'{FIXTURES_ROOT}/data/chen2018/gold.jsonl'
            model_file_path = f'{FIXTURES_ROOT}/data/chen2018/model.jsonl'

            gold = JsonlReader(gold_file_path).read()
            model = JsonlReader(model_file_path).read()

            gold = [[summary['summary']] for summary in gold]
            model = [summary['summary'] for summary in model]

            meteor = Meteor()
            score, _ = meteor.evaluate(model, gold)
            assert score['METEOR'] == pytest.approx(0.1828372, abs=1e-7)
