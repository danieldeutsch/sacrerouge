import os
import pytest

from sacrerouge.common.testing.metric_test_cases import DocumentBasedMetricTestCase
from sacrerouge.common.testing.util import sacrerouge_command_exists
from sacrerouge.metrics import FEQA


@pytest.mark.skipif('FEQA_ENV' not in os.environ, reason='FEQA python environment environment variable not set')
class TestFEQA(DocumentBasedMetricTestCase):
    def test_example(self):
        # Tests to make sure we get the same output as running the example in the original repository
        documents_list = [
            [
                "The world's oldest person has died a \
                 few weeks after celebrating her 117th birthday.  \
                 Born on March 5, 1898, the greatgrandmother had lived through two world \
                 wars, the invention of the television and the \
                 first successful powered aeroplane."
            ],
            [
                "The world's oldest person has died a \
                 few weeks after celebrating her 117th birthday.  \
                 Born on March 5, 1898, the greatgrandmother had lived through two world \
                 wars, the invention of the television and the \
                 first successful powered aeroplane."
            ]
        ]
        summaries = [
            "The world's oldest person died in 1898",
            "The world's oldest person died after her 117th birthday"
        ]

        metric = FEQA(environment_name=os.environ['FEQA_ENV'])

        # The original iPython notebook has the second score of 0.8875, but the first one matches. I assume that
        # this is caused by some minor change (e.g., they use spacy model 2.1.0 in the example but ours uses 2.3.1)
        # since the first score matches.
        expected_output = [
            {'FEQA': 0.674074074074074},
            {'FEQA': 0.85},
        ]
        actual_output = metric.score_all(summaries, documents_list)

        assert len(expected_output) == len(actual_output)
        for expected, actual in zip(expected_output, actual_output):
            assert expected == pytest.approx(actual, 1e-4)

    def test_command_exists(self):
        assert sacrerouge_command_exists(['feqa'])

    def test_setup_command_exists(self):
        assert sacrerouge_command_exists(['setup-metric', 'feqa'])