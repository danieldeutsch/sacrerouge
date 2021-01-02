import pytest

from sacrerouge.common.testing.metric_test_cases import ReferenceBasedMetricTestCase
from sacrerouge.common.testing.util import sacrerouge_command_exists
from sacrerouge.metrics import QAEval
from sacrerouge.metrics.qaeval import QAEVAL_INSTALLED


@pytest.mark.skipif(not QAEVAL_INSTALLED, reason='QAEval not installed')
class TestQAEval(ReferenceBasedMetricTestCase):
    def test_qaeval(self):
        # This is a regression test, not necessarily a test for correctness
        metric = QAEval()
        expected_output = [
            {'qa-eval': {'em': 0.03078358208955224, 'f1': 0.05688114487088367}},
            {'qa-eval': {'em': 0.08286691542288557, 'f1': 0.11367400349443259}},
            {'qa-eval': {'em': 0.05223880597014925, 'f1': 0.10360696517412935}},
            {'qa-eval': {'em': 0.04582555970149253, 'f1': 0.05402803689883914}},
            {'qa-eval': {'em': 0.025276841598459315, 'f1': 0.04173576561636263}},
            {'qa-eval': {'em': 0.029159756771697066, 'f1': 0.0543755246092705}},
            {'qa-eval': {'em': 0.05223880597014925, 'f1': 0.09381412591922542}},
            {'qa-eval': {'em': 0.04537794896485315, 'f1': 0.12145356515842792}},
            {'qa-eval': {'em': 0.06434837092731831, 'f1': 0.10272833079850623}},
            {'qa-eval': {'em': 0.09642160957950431, 'f1': 0.13482779720666102}},
            {'qa-eval': {'em': 0.12349624060150374, 'f1': 0.16393273976257167}},
            {'qa-eval': {'em': 0.12678571428571428, 'f1': 0.16151234567901235}}
        ]
        super().assert_expected_output(metric, expected_output)

    def test_qaeval_with_lerc(self):
        # This is a regression test, not necessarily a test for correctness
        metric = QAEval(use_lerc=True)
        expected_output = [
            {'qa-eval': {'em': 0.03078358208955224, 'f1': 0.05688114487088367, 'lerc': 0.5280342313984585}},
            {'qa-eval': {'em': 0.08286691542288557, 'f1': 0.11367400349443259, 'lerc': 0.8588525844061404}},
            {'qa-eval': {'em': 0.05223880597014925, 'f1': 0.10360696517412935, 'lerc': 1.2307390170310861}},
            {'qa-eval': {'em': 0.04582555970149253, 'f1': 0.05402803689883914, 'lerc': 0.6782244059549116}},
            {'qa-eval': {'em': 0.025276841598459315, 'f1': 0.04173576561636263, 'lerc': 0.40871678001285994}},
            {'qa-eval': {'em': 0.029159756771697066, 'f1': 0.0543755246092705, 'lerc': 0.6477515654560587}},
            {'qa-eval': {'em': 0.05223880597014925, 'f1': 0.09381412591922542, 'lerc': 0.947292007320556}},
            {'qa-eval': {'em': 0.04537794896485315, 'f1': 0.12145356515842792, 'lerc': 1.2629075305115793}},
            {'qa-eval': {'em': 0.06434837092731831, 'f1': 0.10272833079850623, 'lerc': 1.1977039740821571}},
            {'qa-eval': {'em': 0.09642160957950431, 'f1': 0.13482779720666102, 'lerc': 1.2360802221434326}},
            {'qa-eval': {'em': 0.12349624060150374, 'f1': 0.16393273976257167, 'lerc': 1.5575424717221045}},
            {'qa-eval': {'em': 0.12678571428571428, 'f1': 0.16151234567901235, 'lerc': 1.4713040575976408}}
        ]
        super().assert_expected_output(metric, expected_output)

    def test_qaeval_order_invariant(self):
        metric = QAEval()
        self.assert_order_invariant(metric)

    def test_return_qa_pairs(self):
        metric = QAEval(use_lerc=True)

        summaries = [
            'Dan walked to the bakery this morning.',
            'He bought some scones today'
        ]
        reference = 'Dan went to buy scones earlier this morning.'

        results_list = metric.score_multi(summaries, [reference], return_qa_pairs=True)
        assert len(results_list) == 2
        metrics, qa_pairs_list = results_list[0]
        assert metrics['qa-eval']['em'] == 0.5
        assert metrics['qa-eval']['f1'] == 0.5
        self.assertAlmostEqual(metrics['qa-eval']['lerc'], 3.171376943588257, places=4)
        assert len(qa_pairs_list) == 1
        qa_pairs = qa_pairs_list[0]
        assert len(qa_pairs) == 2
        assert qa_pairs[0]['question']['question'] == 'Who went to buy scones earlier this morning?'
        assert qa_pairs[0]['prediction']['prediction'] == 'Dan'
        assert qa_pairs[0]['prediction']['em'] == 1.0
        assert qa_pairs[0]['prediction']['f1'] == 1.0
        self.assertAlmostEqual(qa_pairs[0]['prediction']['lerc'], 5.035197734832764, places=4)
        assert qa_pairs[1]['question']['question'] == 'What did Dan go to buy earlier this morning?'
        assert qa_pairs[1]['prediction']['prediction'] == 'bakery'
        assert qa_pairs[1]['prediction']['em'] == 0.0
        assert qa_pairs[1]['prediction']['f1'] == 0.0
        self.assertAlmostEqual(qa_pairs[1]['prediction']['lerc'], 1.30755615234375, places=4)

        metrics, qa_pairs_list = results_list[1]
        assert metrics['qa-eval']['em'] == 0.5
        assert metrics['qa-eval']['f1'] == 0.5
        self.assertAlmostEqual(metrics['qa-eval']['lerc'], 2.492440700531006, places=4)
        assert len(qa_pairs_list) == 1
        qa_pairs = qa_pairs_list[0]
        assert len(qa_pairs) == 2
        assert qa_pairs[0]['question']['question'] == 'Who went to buy scones earlier this morning?'
        assert qa_pairs[0]['prediction']['prediction'] == 'He'
        assert qa_pairs[0]['prediction']['em'] == 0.0
        assert qa_pairs[0]['prediction']['f1'] == 0.0
        assert qa_pairs[0]['prediction']['lerc'] == 0.0
        assert qa_pairs[1]['question']['question'] == 'What did Dan go to buy earlier this morning?'
        assert qa_pairs[1]['prediction']['prediction'] == 'scones'
        assert qa_pairs[1]['prediction']['em'] == 1.0
        assert qa_pairs[1]['prediction']['f1'] == 1.0
        self.assertAlmostEqual(qa_pairs[1]['prediction']['lerc'], 4.984881401062012, places=4)

    def test_command_exists(self):
        assert sacrerouge_command_exists(['qa-eval'])

    def test_setup_command_exists(self):
        assert sacrerouge_command_exists(['setup-metric', 'qa-eval'])