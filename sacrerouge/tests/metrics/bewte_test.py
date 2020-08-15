import pytest

from sacrerouge.common.testing.metric_test_cases import ReferenceBasedMetricTestCase
from sacrerouge.metrics import BEwTE


@pytest.mark.skip()
class TestBEwTE(ReferenceBasedMetricTestCase):
    def test_bewte(self):
        # This is a regression test, not necessarily a test for correctness
        metric = BEwTE()
        expected_output = [
            {'BEwTE': {'precision': 58.333333333333336, 'recall': 16.800026705054066, 'f1': 26.07284061784773}},
            {'BEwTE': {'precision': 55.89225589225589, 'recall': 21.980295867884113, 'f1': 31.530200681844374}},
            {'BEwTE': {'precision': 71.60493827160494, 'recall': 24.180778925693186, 'f1': 36.14481602051889}},
            {'BEwTE': {'precision': 94.73684210526315, 'recall': 14.080380426445775, 'f1': 24.51308511132803}},
            {'BEwTE': {'precision': 65.4320987654321, 'recall': 14.85657500131804, 'f1': 24.214746840570047}},
            {'BEwTE': {'precision': 66.66666666666667, 'recall': 15.960095884065504, 'f1': 25.754182379367673}},
            {'BEwTE': {'precision': 67.03296703296704, 'recall': 25.78309375670457, 'f1': 37.24173938987096}},
            {'BEwTE': {'precision': 70.11494252873564, 'recall': 25.530979675082634, 'f1': 37.43109567318583}},
            {'BEwTE': {'precision': 65.625, 'recall': 18.55307985024375, 'f1': 28.909233457557765}},
            {'BEwTE': {'precision': 64.15770609318996, 'recall': 26.57395089577402, 'f1': 37.55120996500307}},
            {'BEwTE': {'precision': 74.39024390243902, 'recall': 27.50242072137497, 'f1': 40.0979020979021}},
            {'BEwTE': {'precision': 75.39682539682539, 'recall': 21.900485858060037, 'f1': 33.92688205487086}}
        ]
        super().assert_expected_output(metric, expected_output)

    def test_bewte_order_invariant(self):
        metric = BEwTE()
        self.assert_order_invariant(metric)