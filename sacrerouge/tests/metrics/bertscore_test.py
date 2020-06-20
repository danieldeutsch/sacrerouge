import unittest

from sacrerouge.common.testing.metric_test_cases import ReferenceBasedMetricTestCase
from sacrerouge.metrics import BertScore
from sacrerouge.metrics.bertscore import BERTSCORE_INSTALLED


@unittest.skipIf(not BERTSCORE_INSTALLED, '"bert_score" not installed')
class TestBertScore(ReferenceBasedMetricTestCase):
    def test_bertscore(self):
        # This is a regression test, not necessarily a test for correctness
        metric = BertScore()
        expected_output = [
            {'bertscore': {'precision': 0.8534530401229858, 'recall': 0.8503388166427612, 'f1': 0.8518930673599243}},
            {'bertscore': {'precision': 0.8642909526824951, 'recall': 0.8720692992210388, 'f1': 0.8681626319885254}},
            {'bertscore': {'precision': 0.8623127341270447, 'recall': 0.8670819997787476, 'f1': 0.8646908402442932}},
            {'bertscore': {'precision': 0.8549671173095703, 'recall': 0.856684148311615, 'f1': 0.8558247685432434}},
            {'bertscore': {'precision': 0.8397505283355713, 'recall': 0.8507593870162964, 'f1': 0.8451763987541199}},
            {'bertscore': {'precision': 0.8410190343856812, 'recall': 0.8510528206825256, 'f1': 0.8460061550140381}},
            {'bertscore': {'precision': 0.8653707504272461, 'recall': 0.8665218949317932, 'f1': 0.8659459948539734}},
            {'bertscore': {'precision': 0.868201494216919, 'recall': 0.8704793453216553, 'f1': 0.8693389296531677}},
            {'bertscore': {'precision': 0.9007625579833984, 'recall': 0.8653964400291443, 'f1': 0.8827253580093384}},
            {'bertscore': {'precision': 0.8833473920822144, 'recall': 0.8772095441818237, 'f1': 0.8802677989006042}},
            {'bertscore': {'precision': 0.8683465719223022, 'recall': 0.8797310590744019, 'f1': 0.8740017414093018}},
            {'bertscore': {'precision': 0.8667279481887817, 'recall': 0.8681085109710693, 'f1': 0.8665944337844849}}
        ]
        super().assert_expected_output(metric, expected_output)

    def test_bertscore_idf(self):
        # This is a regression test, not necessarily a test for correctness
        metric = BertScore(idf=True)
        expected_output = [
            {'bertscore': {'precision': 0.8256407976150513, 'recall': 0.8295320272445679, 'f1': 0.8275818228721619}},
            {'bertscore': {'precision': 0.828471302986145, 'recall': 0.8554045557975769, 'f1': 0.8417225480079651}},
            {'bertscore': {'precision': 0.838839054107666, 'recall': 0.8432000279426575, 'f1': 0.8410139083862305}},
            {'bertscore': {'precision': 0.831351637840271, 'recall': 0.8347938060760498, 'f1': 0.8330692052841187}},
            {'bertscore': {'precision': 0.808471143245697, 'recall': 0.8274324536323547, 'f1': 0.8178418874740601}},
            {'bertscore': {'precision': 0.8056685924530029, 'recall': 0.8246532678604126, 'f1': 0.8150504231452942}},
            {'bertscore': {'precision': 0.8379611968994141, 'recall': 0.8408616781234741, 'f1': 0.8390330076217651}},
            {'bertscore': {'precision': 0.8419498205184937, 'recall': 0.8478491902351379, 'f1': 0.8448891639709473}},
            {'bertscore': {'precision': 0.8836315870285034, 'recall': 0.8468402624130249, 'f1': 0.8648448586463928}},
            {'bertscore': {'precision': 0.8534250855445862, 'recall': 0.8621121644973755, 'f1': 0.8577466011047363}},
            {'bertscore': {'precision': 0.8462548851966858, 'recall': 0.8589195013046265, 'f1': 0.852540135383606}},
            {'bertscore': {'precision': 0.8441416621208191, 'recall': 0.8447036743164062, 'f1': 0.8444225788116455}}
        ]
        super().assert_expected_output(metric, expected_output)

    def test_bertscore_order_invariant(self):
        metric = BertScore()
        self.assert_order_invariant(metric)
