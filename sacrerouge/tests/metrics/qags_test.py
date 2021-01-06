import os
import pytest

from sacrerouge.common.testing import FIXTURES_ROOT
from sacrerouge.common.testing.metric_test_cases import DocumentBasedMetricTestCase
from sacrerouge.common.testing.util import sacrerouge_command_exists
from sacrerouge.io import JsonlReader
from sacrerouge.metrics import QAGS


@pytest.mark.skipif('QAGS_ENV' not in os.environ, reason='QAGS python environment environment variable not set')
class TestQAGS(DocumentBasedMetricTestCase):
    def test_example(self):
        instances = JsonlReader(f'{FIXTURES_ROOT}/data/wang2020/summaries.jsonl').read()
        documents_list = []
        summaries = []
        for instance in instances:
            documents_list.append([instance['document']['text']])
            summaries.append(instance['summary']['text'])

        metric = QAGS(environment_name=os.environ['QAGS_ENV'])
        expected_output = [
            {"QAGS": 0.6},
            {"QAGS": 0.8},
            {"QAGS": 0.8},
            {"QAGS": 0.4},
            {"QAGS": 0.8}
        ]
        actual_output = metric.score_all(summaries, documents_list)

        # Sometimes the metric outputs different scores, so this test may fail
        for expected, actual in zip(expected_output, actual_output):
            assert expected == pytest.approx(actual, 1e-4)

    def test_command_exists(self):
        assert sacrerouge_command_exists(['qags'])

    def test_setup_command_exists(self):
        assert sacrerouge_command_exists(['setup-metric', 'qags'])