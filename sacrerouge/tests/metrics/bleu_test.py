from sacrerouge.common.testing.metric_test_cases import ReferenceBasedMetricTestCase
from sacrerouge.common.testing.util import sacrerouge_command_exists
from sacrerouge.metrics import SentBleu


class TestSentBleu(ReferenceBasedMetricTestCase):
    def test_sent_bleu(self):
        # This is a regression test, not necessarily a test for correctness
        metric = SentBleu()
        expected_output = [
            {'sent-bleu': 20.387578585461366},
            {'sent-bleu': 32.896772970823626},
            {'sent-bleu': 18.547566570806502},
            {'sent-bleu': 10.143110526324998},
            {'sent-bleu': 12.741075976084264},
            {'sent-bleu': 13.419295173492271},
            {'sent-bleu': 22.182580005249864},
            {'sent-bleu': 19.000050085118882},
            {'sent-bleu': 19.967094594571897},
            {'sent-bleu': 34.597558358595585},
            {'sent-bleu': 27.126337736450758},
            {'sent-bleu': 18.630200236940578}
        ]
        super().assert_expected_output(metric, expected_output)

    def test_sent_bleu_examples(self):
        # Tests examples from the Github repo and reproduced here:
        # https://colab.research.google.com/drive/1-a_2Y81UE5D-vP3di_cTKG3gIRBQWkdd?usp=sharing
        bleu = SentBleu()

        hypothesis = 'The dog bit the man.'
        references = ['The dog bit the man.', 'The dog had bit the man.']
        expected = 100.0
        actual = bleu.score(hypothesis, references)['sent-bleu']
        self.assertAlmostEqual(expected, actual)

        hypothesis = 'It wasn\'t surprising.'
        references = ['It was not unexpected.', 'No one was surprised.']
        expected = 14.794015674776452
        actual = bleu.score(hypothesis, references)['sent-bleu']
        self.assertAlmostEqual(expected, actual)

        hypothesis = 'The man had just bitten him.'
        references = ['The man bit him first.', 'The man had bitten the dog.']
        expected = 29.071536848410968
        actual = bleu.score(hypothesis, references)['sent-bleu']
        self.assertAlmostEqual(expected, actual)

    def test_sent_bleu_order_invariant(self):
        metric = SentBleu()
        self.assert_order_invariant(metric)

    def test_command_exists(self):
        assert sacrerouge_command_exists(['sent-bleu'])
