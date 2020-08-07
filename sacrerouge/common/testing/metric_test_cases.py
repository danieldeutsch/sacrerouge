import unittest
from typing import List

from sacrerouge.common.testing import MULTILING_SUMMARIES
from sacrerouge.data import MetricsDict
from sacrerouge.io import JsonlReader
from sacrerouge.metrics import Metric


class MetricTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.summaries = []
        cls.references_list = []
        with JsonlReader(MULTILING_SUMMARIES) as f:
            for instance in f:
                cls.summaries.append(instance['summary']['text'])
                references = []
                for reference in instance['references']:
                    references.append(reference['text'])
                cls.references_list.append(references)

    def _assert_expected_output(self, metric: Metric, expected_output: List[MetricsDict], *args, num_summaries: int = None):
        """Ensures that the output from `score_all` is equal to the `expected_output`."""
        summaries = self.summaries if num_summaries is None else self.summaries[:num_summaries]
        assert len(summaries) == len(expected_output)
        actual_output = metric.score_all(summaries, *args)
        for i, (expected, actual) in enumerate(zip(expected_output, actual_output)):
            assert actual.approx_equal(MetricsDict(expected), abs=1e-4), f'Instance {i} not equal. Expected {expected}, actual {actual}'

    def _assert_order_invariant(self, metric: Metric, *args, num_summaries: int = None):
        """Ensures that the output from `score_multi_all` returns the same results, no matter the order."""
        # Reverse the summaries to create a new fake set of summaries that will be grouped together
        # with the same references. It does not matter that they're not the right references since we are
        # only testing to make sure the output doesn't change.
        summaries = self.summaries if num_summaries is None else self.summaries[:num_summaries]
        faked = list(reversed(summaries))

        summaries_list = list(zip(*[summaries, faked]))
        metrics_lists1 = metric.score_multi_all(summaries_list, *args)
        metrics_lists1 = list(zip(*metrics_lists1))

        summaries_list = list(zip(*[faked, summaries]))
        metrics_lists2 = metric.score_multi_all(summaries_list, *args)
        metrics_lists2 = list(zip(*metrics_lists2))

        metrics_lists2 = list(reversed(metrics_lists2))
        for metrics_list1, metrics_list2 in zip(metrics_lists1, metrics_lists2):
            for metrics1, metrics2 in zip(metrics_list1, metrics_list2):
                assert metrics1.approx_equal(metrics2)


class ReferenceBasedMetricTestCase(MetricTestCase):
    def assert_expected_output(self, metric: Metric, expected_output: List[MetricsDict], num_summaries: int = None):
        references_list = self.references_list if num_summaries is None else self.references_list[:num_summaries]
        self._assert_expected_output(metric, expected_output, references_list, num_summaries=num_summaries)

    def assert_order_invariant(self, metric: Metric, num_summaries: int = None):
        references_list = self.references_list if num_summaries is None else self.references_list[:num_summaries]
        self._assert_order_invariant(metric, references_list, num_summaries=num_summaries)


class ReferencelessMetricTestCase(MetricTestCase):
    def assert_expected_output(self, metric: Metric, expected_output: List[MetricsDict]):
        self._assert_expected_output(metric, expected_output)

    def assert_order_invariant(self, metric: Metric):
        self._assert_order_invariant(metric)