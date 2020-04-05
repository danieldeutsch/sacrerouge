import os
import pytest
import unittest

from sacrerouge.data import Pyramid
from sacrerouge.io import JsonlReader

_pyramids_file_path = 'datasets/duc-tac/tac2008/v1.0/task1.A.pyramids.jsonl'


@pytest.mark.skipif(not os.path.exists(_pyramids_file_path), reason='TAC 2008 pyramids file does not exist')
class TestPyramid(unittest.TestCase):
    def setUp(self):
        self.pyramid = None
        for pyramid in JsonlReader(_pyramids_file_path, Pyramid).read():
            if pyramid.instance_id == 'd0801-A':
                self.pyramid = pyramid
                break

    def test_get_scu_id_set(self):
        assert self.pyramid.get_scu_id_set(0) == set([11, 14, 15, 16, 22, 23, 25, 27, 29, 32, 33, 47])
        assert self.pyramid.get_scu_id_set(1) == set([11, 12, 21, 32, 35, 36, 37, 38, 39, 43, 46])
        assert self.pyramid.get_scu_id_set(2) == set([11, 12, 14, 15, 16, 19, 20, 24, 29, 32, 35])
        assert self.pyramid.get_scu_id_set(3) == set([11, 12, 14, 19, 21, 22, 23, 27, 39, 42, 44, 45])

    def test_remove_summary(self):
        pyramid = self.pyramid.remove_summary(0)
        assert pyramid.summarizer_ids == ['C', 'E', 'G']
        assert len(pyramid.summaries) == 3
        assert pyramid.summaries[0].startswith('Emirate Airlines ordered the first passenger')
        assert pyramid.summaries[1].startswith('The largest passenger airliner ever built')
        assert pyramid.summaries[2].startswith('In 1994 Airbus began engineering')

        assert pyramid.get_scu_id_set(0) == set([11, 12, 21, 32, 35, 36, 37, 38, 39, 43, 46])
        assert pyramid.get_scu_id_set(1) == set([11, 12, 14, 15, 16, 19, 20, 24, 29, 32, 35])
        assert pyramid.get_scu_id_set(2) == set([11, 12, 14, 19, 21, 22, 23, 27, 39, 42, 44, 45])

        # Make sure some old SCUs unique to the removed summary aren't there
        scu_ids = set([scu.scu_id for scu in pyramid.scus])
        assert 33 not in scu_ids
        assert 47 not in scu_ids

    def test_get_annotation(self):
        annotation = self.pyramid.get_annotation(0)
        assert annotation.instance_id == self.pyramid.instance_id
        assert annotation.summarizer_id == self.pyramid.summarizer_ids[0]
        assert annotation.summarizer_type == 'reference'
        assert annotation.summary.startswith('The European Airbus A380 flew its maiden')
        assert len(annotation.scus) == 12
        assert annotation.get_scu_id_set() == set([11, 14, 15, 16, 22, 23, 25, 27, 29, 32, 33, 47])
