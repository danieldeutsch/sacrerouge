import unittest

from sacrerouge.score import average_jackknifing_metrics, get_jackknifing_references_list


class TestScore(unittest.TestCase):
    def test_get_jackknifing_references_list(self):
        references = ['A', 'B', 'C', 'D']
        jk_references_list = get_jackknifing_references_list(references)

        assert len(jk_references_list) == 4
        assert ['A', 'B', 'C'] in jk_references_list
        assert ['B', 'C', 'D'] in jk_references_list
        assert ['A', 'C', 'D'] in jk_references_list
        assert ['A', 'B', 'D'] in jk_references_list

    def test_average_jackknifing_metrics(self):
        metrics_list = [
            {
                'a': 2,
                'b': {
                    'c': 4,
                    'd': 6
                }
            },
            {
                'a': 4,
                'b': {
                    'c': 10,
                    'd': 12
                }
            }
        ]
        average = average_jackknifing_metrics(metrics_list)
        assert average == {
            'a': 3,
            'b': {
                'c': 7,
                'd': 9
            }
        }
