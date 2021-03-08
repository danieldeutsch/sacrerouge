import unittest

from sacrerouge.common.testing.metric_test_cases import DocumentBasedMetricTestCase
from sacrerouge.common.testing.util import sacrerouge_command_exists
from sacrerouge.metrics import Blanc
from sacrerouge.metrics.blanc import BLANC_INSTALLED


@unittest.skipIf(not BLANC_INSTALLED, '"blanc" not installed')
class TestBlanc(DocumentBasedMetricTestCase):
    def test_command_exists(self):
        assert sacrerouge_command_exists(['blanc'])

    def test_setup_command_exists(self):
        assert sacrerouge_command_exists(['setup-metric', 'blanc'])

    def test_blanc_help_regression(self):
        # Tests the examples from the official github repo, but they do not match the scores there and I don't know why
        metric = Blanc(blanc_type='blanc_help', random_seed=4)
        documents_list = [
            ['Jack drove his minivan to the bazaar to purchase milk and honey for his large family.'],
            ['As Jill started taking a walk in the park, she certainly noticed that the trees were extra green this year.']
        ]
        summaries_list = [
            ['Jack bought milk and honey.', 'Jack drove to the bazaar in a minivan'],
            ['Jill saw green trees in the park.', 'The trees were green.']
        ]
        expected_scores_list = [
            [0.2222222222222222, 0.2222222222222222],
            [0.14285714285714285, 0.14285714285714285]
        ]
        actual_scores_list = metric.score_multi_all(summaries_list, documents_list)

        assert len(expected_scores_list) == len(actual_scores_list)
        for expected_scores, actual_scores in zip(expected_scores_list, actual_scores_list):
            assert len(expected_scores) == len(actual_scores)
            for expected, actual in zip(expected_scores, actual_scores):
                self.assertAlmostEqual(expected, actual['blanc_help'], places=4)

    def test_blanc_tune_repo(self):
        # Tests the examples from the official github repo. The scores don't match because they change based
        # on the random seed and the repo does not set the random seed
        metric = Blanc(blanc_type='blanc_tune', gap=6)
        documents_list = [
            ['Jack drove his minivan to the bazaar to purchase milk and honey for his large family.'],
            ['As Jill started taking a walk in the park, she certainly noticed that the trees were extra green this year.']
        ]
        summaries_list = [
            ['Jack bought milk and honey.', 'Jack drove to the bazaar in a minivan'],
            ['Jill saw green trees in the park.', 'The trees were green.']
        ]
        # The github repo shows the last 2 numbers are negative in some spots, but positive in others. I think
        # they're supposed to be positive
        expected_scores_list = [
            [0.1111111111111111, 0.2222222222222222],
            [0.14285714285714285, 0.14285714285714285]
        ]
        actual_scores_list = metric.score_multi_all(summaries_list, documents_list)

        assert len(expected_scores_list) == len(actual_scores_list)
        for expected_scores, actual_scores in zip(expected_scores_list, actual_scores_list):
            assert len(expected_scores) == len(actual_scores)
            for expected, actual in zip(expected_scores, actual_scores):
                self.assertAlmostEqual(expected, actual['blanc_tune'], places=4)
