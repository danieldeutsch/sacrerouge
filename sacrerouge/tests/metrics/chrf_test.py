from sacrerouge.common.testing.metric_test_cases import ReferenceBasedMetricTestCase
from sacrerouge.common.testing.util import sacrerouge_command_exists
from sacrerouge.metrics.chrf import ChrF


class TestChrF(ReferenceBasedMetricTestCase):
    def test_chrf(self):
        # This is a regression test, not necessarily a test for correctness
        metric = ChrF()
        expected_output = [
            {'chrf': 43.85388187268078},
            {'chrf': 52.60988684061151},
            {'chrf': 49.65855270200033},
            {'chrf': 41.43422564802467},
            {'chrf': 42.53477752245672},
            {'chrf': 41.91433502501302},
            {'chrf': 49.91729287293663},
            {'chrf': 49.63089847829706},
            {'chrf': 43.484464138558174},
            {'chrf': 56.073961048238665},
            {'chrf': 48.94445553665466},
            {'chrf': 46.85719853900437}
        ]
        super().assert_expected_output(metric, expected_output)

    def test_chrf_examples(self):
        chrf = ChrF()

        hypothesis = 'The dog bit the man.'
        references = ['The dog bit the man.', 'The dog had bit the man.']
        expected = 100.0
        actual = chrf.score(hypothesis, references)['chrf']
        self.assertAlmostEqual(expected, actual)

        hypothesis = 'It wasn\'t surprising.'
        references = ['It was not unexpected.', 'No one was surprised.']
        expected = 35.34635301425291
        actual = chrf.score(hypothesis, references)['chrf']
        self.assertAlmostEqual(expected, actual)

        hypothesis = 'The man had just bitten him.'
        references = ['The man bit him first.', 'The man had bitten the dog.']
        expected = 51.87740799504779
        actual = chrf.score(hypothesis, references)['chrf']
        self.assertAlmostEqual(expected, actual)

    def test_chrf_order_invariant(self):
        metric = ChrF()
        self.assert_order_invariant(metric)

    def test_command_exists(self):
        assert sacrerouge_command_exists(['chrf'])
