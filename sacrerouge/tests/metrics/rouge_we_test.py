import unittest

from sacrerouge.metrics import RougeWE


class TestRougeWE(unittest.TestCase):
    def test_rouge_we(self):
        """Make sure ROUGE-WE runs"""
        # From the ROUGE-WE repository
        summaries = [
            'New York and Portugal have different weather systems. Portugal has less extremes in temperatures.',
            'The quick brown fox jumps over the lazy dog. So what does the fox say?',
        ]
        references_list = [
            [
                'New York has a harsher climate than Portugal. It has more frigid winters and warmer summers.',
                'Portugal has a milder climate than New York. Summers are less warm and winters are less cold.'
            ],
            [
                'New York has a harsher climate than Portugal. It has more frigid winters and warmer summers.',
                'Portugal has a milder climate than New York. Summers are less warm and winters are less cold.'
            ]
        ]

        rouge = RougeWE()
        _, metrics_list = rouge.score_all(summaries, references_list)
