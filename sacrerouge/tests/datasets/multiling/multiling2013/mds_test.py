import os
import pytest
import unittest
from glob import glob

from sacrerouge.io import JsonlReader

_mds_dir = 'datasets/multiling/multiling2013/mds'


@pytest.mark.skipif(not os.path.exists(_mds_dir), reason='MultiLing 2013 MDS data does not exist')
class TestMultiLing2013MDS(unittest.TestCase):
    def test_sanity_checks(self):
        file_paths = glob(f'{_mds_dir}/*.jsonl')
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