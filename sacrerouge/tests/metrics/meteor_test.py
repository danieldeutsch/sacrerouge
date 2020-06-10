import pytest
import unittest

from sacrerouge.common.testing import FIXTURES_ROOT, load_references, load_summaries
from sacrerouge.io import JsonlReader
from sacrerouge.metrics import Meteor

_duc2004_file_path = 'datasets/duc-tac/duc2004/v1.0/task2.jsonl'
_centroid_file_path = f'{FIXTURES_ROOT}/data/hong2014/centroid.jsonl'


class TestMeteor(unittest.TestCase):
        def test_meteor(self):
            """Verify METEOR runs"""
            # These numbers aren't verified to be correct, but will catch if
            # the code changes
            meteor = Meteor()
            duc2004 = load_references(_duc2004_file_path)
            centroid = load_summaries(_centroid_file_path)

            system_score, summary_scores = meteor.evaluate(centroid, duc2004)
            assert system_score == pytest.approx({'METEOR': 0.16913291651219267}, abs=1e-4)
            assert summary_scores[:5] == pytest.approx([
                {'METEOR': 0.19100187219134385},
                {'METEOR': 0.155452410194115},
                {'METEOR': 0.1840667990852698},
                {'METEOR': 0.18111121583550865},
                {'METEOR': 0.13502476502555888}
            ], abs=1e-5)

        def test_score_multi_all_order(self):
            """Tests to ensure the scoring returns the same results, no matter the order."""
            meteor = Meteor()
            duc2004 = load_references(_duc2004_file_path)
            centroid1 = load_summaries(_centroid_file_path)
            centroid2 = list(reversed(centroid1))  # Just create a second fake dataset

            summaries_list = list(zip(*[centroid1, centroid2]))
            metrics_lists1 = meteor.score_multi_all(summaries_list, duc2004)
            metrics_lists1 = list(zip(*metrics_lists1))

            summaries_list = list(zip(*[centroid2, centroid1]))
            metrics_lists2 = meteor.score_multi_all(summaries_list, duc2004)
            metrics_lists2 = list(zip(*metrics_lists2))

            metrics_lists2 = list(reversed(metrics_lists2))
            assert metrics_lists1 == metrics_lists2

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
