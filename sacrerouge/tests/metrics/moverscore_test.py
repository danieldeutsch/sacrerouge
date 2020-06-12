import pytest

from sacrerouge.common.testing.metric_test_cases import ReferenceBasedMetricTestCase
from sacrerouge.metrics import MoverScore
from sacrerouge.metrics.moverscore import MOVERSCORE_INSTALLED


@pytest.mark.skipif(not MOVERSCORE_INSTALLED, reason='MoverScore not setup')
class TestMoverScore(ReferenceBasedMetricTestCase):
    def test_moverscore(self):
        # This is a regression test, not necessarily a test for correctness
        metric = MoverScore()
        expected_output = [
            {'MoverScore': 0.13538047261472216},
            {'MoverScore': 0.19151070384024393},
            {'MoverScore': 0.21223604036747462},
            {'MoverScore': 0.17447731600410432},
            {'MoverScore': 0.1479818362434758},
            {'MoverScore': 0.14823672247671074},
            {'MoverScore': 0.22382319193839145},
            {'MoverScore': 0.23362081109521693},
            {'MoverScore': 0.20162050907949902},
            {'MoverScore': 0.24070720220937813},
            {'MoverScore': 0.22734330926367746},
            {'MoverScore': 0.18901058452094593}
        ]
        super().assert_expected_output(metric, expected_output)

    def test_moverscore_order_invariant(self):
        metric = MoverScore()
        self.assert_order_invariant(metric)
