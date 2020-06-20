import os
import pytest
import unittest
from glob import glob

from sacrerouge.io import JsonlReader

_sds_dir = 'datasets/multiling/multiling2015/sds'


@pytest.mark.skipif(not os.path.exists(_sds_dir), reason='MultiLing 2015 SDS data does not exist')
class TestMultiLing2015SDS(unittest.TestCase):
    def test_sanity_checks(self):
        file_paths = glob(f'{_sds_dir}/*.jsonl')
        assert len(file_paths) == 38  # 38 languages

        # Make sure each one has 30 instances with non-empty documents and summaries
        for file_path in file_paths:
            instances = JsonlReader(file_path).read()
            assert len(instances) == 30
            for instance in instances:
                assert len(instance['document']) > 0
                assert len(instance['summary']) > 0