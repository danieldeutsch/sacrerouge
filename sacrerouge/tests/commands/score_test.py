import unittest

from sacrerouge.commands.score import get_jackknifing_references_list


class TestScore(unittest.TestCase):
    def test_get_jackknifing_references_list(self):
        references = ['A', 'B', 'C', 'D']
        jk_references_list = get_jackknifing_references_list(references)

        assert len(jk_references_list) == 4
        assert ['A', 'B', 'C'] in jk_references_list
        assert ['B', 'C', 'D'] in jk_references_list
        assert ['A', 'C', 'D'] in jk_references_list
        assert ['A', 'B', 'D'] in jk_references_list
