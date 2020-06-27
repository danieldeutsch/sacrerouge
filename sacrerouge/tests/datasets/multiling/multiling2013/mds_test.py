import os
import pytest
import unittest
from glob import glob

from sacrerouge.common.testing.util import load_metrics_dicts
from sacrerouge.io import JsonlReader

_mds_dir = 'datasets/multiling/multiling2013/mds'


@pytest.mark.skipif(not os.path.exists(_mds_dir), reason='MultiLing 2013 MDS data does not exist')
class TestMultiLing2013MDS(unittest.TestCase):
    def test_sanity_checks(self):
        file_paths = glob(f'{_mds_dir}/??.jsonl')
        assert len(file_paths) == 10  # 10 languages

        # Make sure each one has non-empty documents and summaries
        for file_path in file_paths:
            instances = JsonlReader(file_path).read()
            for instance in instances:
                assert len(instance['documents']) == 10
                for document in instance['documents']:
                    assert len(document['text']) > 0

                assert len(instance['summaries']) > 0
                for summary in instance['summaries']:
                    assert len(summary['text']) > 0

    def test_metrics(self):
        for language in ['ar', 'es', 'he', 'zh', 'cs', 'ro', 'el', 'en']:
            # Make sure summaries and metrics in parallel
            summaries = JsonlReader(f'{_mds_dir}/{language}.summaries.jsonl').read()
            metrics = JsonlReader(f'{_mds_dir}/{language}.metrics.jsonl').read()
            assert len(summaries) == len(metrics)

            for summary, metrics in zip(summaries, metrics):
                assert summary['instance_id'] == metrics['instance_id']
                assert summary['summarizer_id'] == metrics['summarizer_id']
                assert summary['summarizer_type'] == metrics['summarizer_type']

        # Test a few metrics
        metrics_dicts = load_metrics_dicts(f'{_mds_dir}/en.metrics.jsonl')
        assert metrics_dicts['M000']['ID1']['overall_responsiveness'] == [3.0, 3.0]
        assert metrics_dicts['M006']['ID61']['overall_responsiveness'] == [2.0, 2.0, 2.0]
        assert metrics_dicts['M100']['A']['overall_responsiveness'] == [4.0, 5.0, 5.0]

        metrics_dicts = load_metrics_dicts(f'{_mds_dir}/es.metrics.jsonl')
        assert metrics_dicts['M000']['A']['overall_responsiveness'] == [4.0, 3.0, 3.0]
        assert metrics_dicts['M006']['ID4']['overall_responsiveness'] == [5.0, 3.0, 4.0]
        assert metrics_dicts['M009']['ID2']['overall_responsiveness'] == [4.0, 5.0, 3.0]
