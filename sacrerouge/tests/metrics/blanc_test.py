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

    def test_blanc_help_repo(self):
        # Ensures the metric returns the values from a Colab notebook which runs the examples from
        # the Github repo. The notebook fixes the random seed for blanc_tune. Different values are
        # returned for both versions of Blanc than what is reported in the Github repo, but that
        # is probably due to stale documentation.
        #
        # Colab notebook: https://colab.research.google.com/drive/17pJ94L2kCL6QMBMflOm-H0ApBiOUWJ1H?usp=sharing
        metric = Blanc(blanc_type='blanc_help')

        document = "Jack drove his minivan to the bazaar to purchase milk and honey for his large family."
        summary = "Jack bought milk and honey."
        score = metric.score(summary, [document])
        self.assertAlmostEqual(0.2222222222222222, score['blanc_help'], places=4)

        documents = [["Jack drove his minivan to the bazaar to purchase milk and honey for his large family."],
                     ["As Jill started taking a walk in the park, she certainly noticed that the trees were extra green this year."]]
        summaries = ["Jack bought milk and honey.", "Jill saw green trees in the park."]
        scores = metric.score_all(summaries, documents)
        self.assertAlmostEqual(0.2222222222222222, scores[0]['blanc_help'], places=4)
        self.assertAlmostEqual(0.14285714285714285, scores[1]['blanc_help'], places=4)

    def test_blanc_tune_repo(self):
        # See note in `test_blanc_help_repo`
        metric = Blanc(blanc_type='blanc_tune', finetune_mask_evenly=False)

        document = "Jack drove his minivan to the bazaar to purchase milk and honey for his large family."
        summary = "Jack bought milk and honey."
        score = metric.score(summary, [document])
        self.assertAlmostEqual(0.3333333333333333, score['blanc_tune'], places=4)

        metric = Blanc(
            blanc_type='blanc_tune', inference_batch_size=24, finetune_mask_evenly=False, finetune_batch_size=24
        )
        documents = [["Jack drove his minivan to the bazaar to purchase milk and honey for his large family."],
                     ["As Jill started taking a walk in the park, she certainly noticed that the trees were extra green this year."]]
        doc_summaries = [["Jack bought milk and honey.", "Jack drove to the bazaar in a minivan"], ["Jill saw green trees in the park.", "The trees were green."]]
        scores = metric.score_multi_all(doc_summaries, documents)
        self.assertAlmostEqual(0.0, scores[0][0]['blanc_tune'], places=4)
        self.assertAlmostEqual(0.2222222222222222, scores[0][1]['blanc_tune'], places=4)
        self.assertAlmostEqual(0.14285714285714285, scores[1][0]['blanc_tune'], places=4)
        self.assertAlmostEqual(0.07142857142857142, scores[1][1]['blanc_tune'], places=4)
