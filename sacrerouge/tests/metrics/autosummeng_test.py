from sacrerouge.common.testing.metric_test_cases import ReferenceBasedMetricTestCase
from sacrerouge.metrics import AutoSummENG


class TestAutoSummENG(ReferenceBasedMetricTestCase):
    def test_autosummeng(self):
        # This is a regression test, not necessarily a test for correctness
        metric = AutoSummENG()
        expected_output = [
            {'AutoSummENG': 0.137825, 'MeMoG': 0.15328, 'NPowER': 0.177641},
            {'AutoSummENG': 0.181275, 'MeMoG': 0.168514, 'NPowER': 0.205207},
            {'AutoSummENG': 0.24427, 'MeMoG': 0.269781, 'NPowER': 0.268968},
            {'AutoSummENG': 0.148213, 'MeMoG': 0.151705, 'NPowER': 0.182664},
            {'AutoSummENG': 0.14474, 'MeMoG': 0.178874, 'NPowER': 0.188991},
            {'AutoSummENG': 0.144389, 'MeMoG': 0.155941, 'NPowER': 0.181914},
            {'AutoSummENG': 0.210532, 'MeMoG': 0.207259, 'NPowER': 0.232329},
            {'AutoSummENG': 0.204209, 'MeMoG': 0.20244, 'NPowER': 0.227536},
            {'AutoSummENG': 0.136333, 'MeMoG': 0.127154, 'NPowER': 0.169001},
            {'AutoSummENG': 0.216562, 'MeMoG': 0.22591, 'NPowER': 0.241125},
            {'AutoSummENG': 0.242036, 'MeMoG': 0.251485, 'NPowER': 0.262288},
            {'AutoSummENG': 0.215287, 'MeMoG': 0.21972, 'NPowER': 0.23859}
        ]
        super().assert_expected_output(metric, expected_output)

    def test_autosummeng_order_invariant(self):
        metric = AutoSummENG()
        self.assert_order_invariant(metric)

    def test_commandline_runs(self):
        self.assert_commandline_runs('autosummeng')
