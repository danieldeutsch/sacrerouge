import unittest

from sacrerouge.metrics.qa.answer_selection import AnswerSelector, NP_CHUNKS_STRATEGY, \
    MAX_NP_STRATEGY, NER_STRATEGY, ALL_STRATEGY, STRATEGIES, AnswerOffsets


class TestAnswerSelector(unittest.TestCase):
    def test_constructor(self):
        for strategy in STRATEGIES:
            AnswerSelector(strategy)
        with self.assertRaises(Exception):
            AnswerSelector('missing')

    def test_np_chunks(self):
        selector = AnswerSelector(NP_CHUNKS_STRATEGY)
        answers = selector.select('Several churches in Baghdad have been attacked. More attacks have been in Mosul.')
        assert len(answers) == 4
        assert answers[0] == AnswerOffsets(0, 16, 0, 47)  # Several churches
        assert answers[1] == AnswerOffsets(20, 27, 0, 47)  # Baghdad
        assert answers[2] == AnswerOffsets(48, 60, 48, 80)  # More attacks
        assert answers[3] == AnswerOffsets(74, 79, 48, 80)  # Mosul

    def test_max_np(self):
        selector = AnswerSelector(MAX_NP_STRATEGY)
        answers = selector.select('Several churches in Baghdad have been attacked. More attacks have been in Mosul.')
        assert len(answers) == 3
        assert answers[0] == AnswerOffsets(0, 27, 0, 47)  # Several churches in Baghdad
        assert answers[1] == AnswerOffsets(48, 60, 48, 80)  # More attacks
        assert answers[2] == AnswerOffsets(74, 79, 48, 80)  # Mosul

    def test_ner(self):
        selector = AnswerSelector(NER_STRATEGY)
        answers = selector.select('Several churches in Baghdad have been attacked. More attacks have been in Mosul.')
        assert len(answers) == 2
        assert answers[0] == AnswerOffsets(20, 27, 0, 47)  # Baghdad
        assert answers[1] == AnswerOffsets(74, 79, 48, 80)  # Mosul

    def test_all(self):
        selector = AnswerSelector(ALL_STRATEGY)
        answers = selector.select('Several churches in Baghdad have been attacked. More attacks have been in Mosul.')
        assert len(answers) == 5
        assert answers[0] == AnswerOffsets(0, 16, 0, 47)  # Several churches
        assert answers[1] == AnswerOffsets(0, 27, 0, 47)  # Several churches in Baghdad
        assert answers[2] == AnswerOffsets(20, 27, 0, 47)  # Baghdad
        assert answers[3] == AnswerOffsets(48, 60, 48, 80)  # More attacks
        assert answers[4] == AnswerOffsets(74, 79, 48, 80)  # Mosul
