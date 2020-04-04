import jsons
import unittest

from sacrerouge.data import Metrics, MetricsDict


class TestMetrics(unittest.TestCase):
    def test_serialization(self):
        instance_id = 'd500'
        summarizer_id = '5'
        summarizer_type = 'peer'
        metrics_dict = {'a': 4, 'b': {'c': [1, 2]}}
        metrics = Metrics(instance_id, summarizer_id, summarizer_type, metrics_dict)

        serialized = jsons.dumps(metrics)
        assert serialized == '{"instance_id": "d500", "summarizer_id": "5", "summarizer_type": "peer", "metrics": {"a": 4, "b": {"c": [1, 2]}}}'

        deserialized = jsons.loads(serialized, Metrics)
        assert metrics == deserialized
        assert isinstance(deserialized.metrics, MetricsDict)
