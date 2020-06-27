import os
import pytest
import unittest
from glob import glob

from sacrerouge.io import JsonlReader

_sds_dir = 'datasets/multiling/multiling2017/sds'


@pytest.mark.skipif(not os.path.exists(_sds_dir), reason='MultiLing 2017 SDS data does not exist')
class TestMultiLing2017SDS(unittest.TestCase):
    def test_sanity_checks(self):
        file_paths = glob(f'{_sds_dir}/??.jsonl')
        assert len(file_paths) == 40  # 40 languages

        # Make sure each one has 30 instances with non-empty documents and summaries
        for file_path in file_paths:
            instances = JsonlReader(file_path).read()
            assert len(instances) == 30
            for instance in instances:
                assert len(instance['document']) > 0
                assert len(instance['summary']) > 0

    def test_peer_summaries(self):
        # Run sanity checks on the peer summaries
        for file_path in glob(f'{_sds_dir}/??.summaries.jsonl'):
            instances = JsonlReader(file_path).read()
            for instance in instances:
                assert len(instance['summary']['text']) > 0
                for reference in instance['references']:
                    assert len(reference['text']) > 0