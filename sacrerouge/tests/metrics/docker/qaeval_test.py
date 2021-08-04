import pytest
from repro.common.docker import image_exists

from sacrerouge.common.testing.metric_test_cases import ReferenceBasedMetricTestCase
from sacrerouge.common.testing.util import sacrerouge_command_exists
from sacrerouge.metrics.docker import DockerQAEval


@pytest.mark.skipif(not image_exists("deutsch2021"), reason="Docker image \"deutsch2021\" does not exist")
class TestDockerQAEval(ReferenceBasedMetricTestCase):
    def test_qaeval_with_lerc(self):
        # This is a regression test, not necessarily a test for correctness
        metric = DockerQAEval()
        expected_output = [
            {'qa-eval': {'is_answered': 0.2171952736318408, 'em': 0.03078358208955224, 'f1': 0.05688114487088367, 'lerc': 0.5280342313984585}},
            {'qa-eval': {'is_answered': 0.2706778606965174, 'em': 0.08286691542288557, 'f1': 0.11367400349443259, 'lerc': 0.8588525844061404}},
            {'qa-eval': {'is_answered': 0.4552238805970149, 'em': 0.05223880597014925, 'f1': 0.10360696517412935, 'lerc': 1.2307390170310861}},
            {'qa-eval': {'is_answered': 0.2671408582089552, 'em': 0.04582555970149253, 'f1': 0.05402803689883914, 'lerc': 0.6782244059549116}},
            {'qa-eval': {'is_answered': 0.17126063232225966, 'em': 0.025276841598459315, 'f1': 0.04173576561636263, 'lerc': 0.40871678001285994}},
            {'qa-eval': {'is_answered': 0.3291829383548209, 'em': 0.029159756771697066, 'f1': 0.0543755246092705, 'lerc': 0.6477515654560587}},
            {'qa-eval': {'is_answered': 0.34836235489220563, 'em': 0.05223880597014925, 'f1': 0.09381412591922542, 'lerc': 0.947292007320556}},
            {'qa-eval': {'is_answered': 0.4337987481945113, 'em': 0.04537794896485315, 'f1': 0.12145356515842792, 'lerc': 1.2629075305115793}},
            {'qa-eval': {'is_answered': 0.44427039821776665, 'em': 0.06434837092731831, 'f1': 0.10272833079850623, 'lerc': 1.1977039740821571}},
            {'qa-eval': {'is_answered': 0.40391255917571706, 'em': 0.09642160957950431, 'f1': 0.13482779720666102, 'lerc': 1.2360802221434326}},
            {'qa-eval': {'is_answered': 0.5345864661654135, 'em': 0.12349624060150374, 'f1': 0.16393273976257167, 'lerc': 1.5575424717221045}},
            {'qa-eval': {'is_answered': 0.5204365079365079, 'em': 0.12678571428571428, 'f1': 0.16151234567901235, 'lerc': 1.4713040575976408}}
        ]
        super().assert_expected_output(metric, expected_output)

    def test_qaeval_order_invariant(self):
        metric = DockerQAEval()
        self.assert_order_invariant(metric)

    def test_return_qa_pairs(self):
        metric = DockerQAEval()

        summaries = [
            'Dan walked to the bakery this morning.',
            'He bought some scones today'
        ]
        reference = 'Dan went to buy scones earlier this morning.'

        results_list = metric.score_multi(summaries, [reference], return_qa_pairs=True)
        assert len(results_list) == 2
        metrics, qa_pairs_list = results_list[0]
        assert metrics['qa-eval']['is_answered'] == 1.0
        assert metrics['qa-eval']['em'] == 0.5
        assert metrics['qa-eval']['f1'] == 0.5
        self.assertAlmostEqual(metrics['qa-eval']['lerc'], 3.171376943588257, places=4)
        assert len(qa_pairs_list) == 1
        qa_pairs = qa_pairs_list[0]
        assert len(qa_pairs) == 2
        assert qa_pairs[0]['question']['question'] == 'Who went to buy scones earlier this morning?'
        assert qa_pairs[0]['prediction']['prediction'] == 'Dan'
        assert qa_pairs[0]['prediction']['start'] == 0
        assert qa_pairs[0]['prediction']['end'] == 3
        assert qa_pairs[0]['prediction']['is_answered'] == 1.0
        assert qa_pairs[0]['prediction']['em'] == 1.0
        assert qa_pairs[0]['prediction']['f1'] == 1.0
        self.assertAlmostEqual(qa_pairs[0]['prediction']['lerc'], 5.035197734832764, places=4)
        assert qa_pairs[1]['question']['question'] == 'What did Dan go to buy earlier this morning?'
        assert qa_pairs[1]['prediction']['prediction'] == 'bakery'
        assert qa_pairs[1]['prediction']['start'] == 18
        assert qa_pairs[1]['prediction']['end'] == 24
        assert qa_pairs[1]['prediction']['is_answered'] == 1.0
        assert qa_pairs[1]['prediction']['em'] == 0.0
        assert qa_pairs[1]['prediction']['f1'] == 0.0
        self.assertAlmostEqual(qa_pairs[1]['prediction']['lerc'], 1.30755615234375, places=4)

        metrics, qa_pairs_list = results_list[1]
        assert metrics['qa-eval']['is_answered'] == 0.5
        assert metrics['qa-eval']['em'] == 0.5
        assert metrics['qa-eval']['f1'] == 0.5
        self.assertAlmostEqual(metrics['qa-eval']['lerc'], 2.492440700531006, places=4)
        assert len(qa_pairs_list) == 1
        qa_pairs = qa_pairs_list[0]
        assert len(qa_pairs) == 2
        assert qa_pairs[0]['question']['question'] == 'Who went to buy scones earlier this morning?'
        assert qa_pairs[0]['prediction']['prediction'] == 'He'
        assert qa_pairs[0]['prediction']['start'] == 0
        assert qa_pairs[0]['prediction']['end'] == 2
        assert qa_pairs[0]['prediction']['is_answered'] == 0.0
        assert qa_pairs[0]['prediction']['em'] == 0.0
        assert qa_pairs[0]['prediction']['f1'] == 0.0
        assert qa_pairs[0]['prediction']['lerc'] == 0.0
        assert qa_pairs[1]['question']['question'] == 'What did Dan go to buy earlier this morning?'
        assert qa_pairs[1]['prediction']['prediction'] == 'scones'
        assert qa_pairs[1]['prediction']['start'] == 15
        assert qa_pairs[1]['prediction']['end'] == 21
        assert qa_pairs[1]['prediction']['is_answered'] == 1.0
        assert qa_pairs[1]['prediction']['em'] == 1.0
        assert qa_pairs[1]['prediction']['f1'] == 1.0
        self.assertAlmostEqual(qa_pairs[1]['prediction']['lerc'], 4.984881401062012, places=4)

    def test_command_exists(self):
        assert sacrerouge_command_exists(['docker-qa-eval'])
