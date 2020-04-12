import pytest
import unittest

from sacrerouge.common.testing import FIXTURES_ROOT, load_summaries
from sacrerouge.metrics import SumQE

_centroid_file_path = f'{FIXTURES_ROOT}/data/hong2014/centroid.jsonl'


class TestSumQE(unittest.TestCase):
    def test_sum_qe(self):
        """
        Verify SumQE runs. These scores haven't been tested to be accurate,
        but the test will capture if anything changes with the metric.
        """
        sumqe = SumQE(environment_name='SumQE')
        centroid = load_summaries(_centroid_file_path)

        # It's quite slow, so we only run a few examples here
        centroid = centroid[:5]
        scores = sumqe.score_all(centroid)
        assert scores == pytest.approx(
            [
                {
                    "SumQE": {
                        "Q1": 0.8985345363616943,
                        "Q2": 0.9253203272819519,
                        "Q3": 0.8012534379959106,
                        "Q4": 0.871218204498291,
                        "Q5": 0.6108772158622742
                    }
                },
                {
                    "SumQE": {
                        "Q1": 0.7544711828231812,
                        "Q2": 0.8587688207626343,
                        "Q3": 0.9127543568611145,
                        "Q4": 0.8986099362373352,
                        "Q5": 0.623852014541626
                    }
                },
                {
                    "SumQE": {
                        "Q1": 0.9851462244987488,
                        "Q2": 0.8688598275184631,
                        "Q3": 0.942189633846283,
                        "Q4": 0.8591314554214478,
                        "Q5": 0.5004895925521851
                    }
                },
                {
                    "SumQE": {
                        "Q1": 0.3283337950706482,
                        "Q2": 0.8776571750640869,
                        "Q3": 0.8603634834289551,
                        "Q4": 0.8669484853744507,
                        "Q5": 0.44943714141845703
                    }
                },
                {
                    "SumQE": {
                        "Q1": 0.6950153112411499,
                        "Q2": 1.0309709310531616,
                        "Q3": 0.6369255781173706,
                        "Q4": 0.5551949143409729,
                        "Q5": 0.49241942167282104
                    }
                }], abs=1e-4)

    def test_score_multi_all_order(self):
        """Tests to ensure the scoring returns the same results, no matter the order."""
        sumqe = SumQE(environment_name='SumQE')
        centroid1 = load_summaries(_centroid_file_path)
        # Just test a few because this is a slow metric
        centroid1 = centroid1[:5]
        centroid2 = list(reversed(centroid1))  # Just create a second fake dataset

        summaries_list = list(zip(*[centroid1, centroid2]))
        metrics_lists1 = sumqe.score_multi_all(summaries_list)
        metrics_lists1 = list(zip(*metrics_lists1))

        summaries_list = list(zip(*[centroid2, centroid1]))
        metrics_lists2 = sumqe.score_multi_all(summaries_list)
        metrics_lists2 = list(zip(*metrics_lists2))

        metrics_lists2 = list(reversed(metrics_lists2))
        assert metrics_lists1 == metrics_lists2
