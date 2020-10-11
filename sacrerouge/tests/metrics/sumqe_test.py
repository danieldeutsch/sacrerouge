import os
import pytest

from sacrerouge.common.testing.metric_test_cases import ReferencelessMetricTestCase
from sacrerouge.metrics import SumQE


@pytest.mark.skipif('SUMQE_PYTHON_BINARY' not in os.environ, reason='SumQE python binary environment variable not set')
class TestSumQE(ReferencelessMetricTestCase):
    def test_sum_qe(self):
        # This is a regression test, not necessarily a test for correctness
        metric = SumQE(python_binary=os.environ['SUMQE_PYTHON_BINARY'])
        expected_output = [
            {'SumQE': {'Q1': 0.6114518642425537, 'Q2': 0.8854175806045532, 'Q3': 0.8413561582565308, 'Q4': 0.7688009738922119, 'Q5': 0.5558874011039734}},
            {'SumQE': {'Q1': 0.5558350086212158, 'Q2': 0.9138086438179016, 'Q3': 0.7335574626922607, 'Q4': 0.6305676102638245, 'Q5': 0.3748158812522888}},
            {'SumQE': {'Q1': 0.7050521373748779, 'Q2': 0.9852879047393799, 'Q3': 0.6667071580886841, 'Q4': 0.6230998039245605, 'Q5': 0.42010897397994995}},
            {'SumQE': {'Q1': 0.834473192691803, 'Q2': 0.9017736911773682, 'Q3': 0.7539371252059937, 'Q4': 0.6262732148170471, 'Q5': 0.3776392638683319}},
            {'SumQE': {'Q1': 0.8146878480911255, 'Q2': 0.7144594192504883, 'Q3': 0.5899823904037476, 'Q4': 0.6519718170166016, 'Q5': 0.384965717792511}},
            {'SumQE': {'Q1': 0.6657560467720032, 'Q2': 0.7149282693862915, 'Q3': 0.44480863213539124, 'Q4': 0.5178157091140747, 'Q5': 0.18973197042942047}},
            {'SumQE': {'Q1': 0.8427770137786865, 'Q2': 0.7266125082969666, 'Q3': 0.7046592831611633, 'Q4': 0.7370807528495789, 'Q5': 0.4456597864627838}},
            {'SumQE': {'Q1': 0.5885571241378784, 'Q2': 0.6695594787597656, 'Q3': 0.33270642161369324, 'Q4': 0.5293599367141724, 'Q5': 0.15236596763134003}},
            {'SumQE': {'Q1': 0.7803599238395691, 'Q2': 0.7456241250038147, 'Q3': 0.7939270734786987, 'Q4': 0.9066981077194214, 'Q5': 0.5868825316429138}},
            {'SumQE': {'Q1': 0.7865289449691772, 'Q2': 0.7511206865310669, 'Q3': 0.6407886147499084, 'Q4': 0.7537230849266052, 'Q5': 0.4621696174144745}},
            {'SumQE': {'Q1': 0.8352774381637573, 'Q2': 0.8135120272636414, 'Q3': 0.6002302169799805, 'Q4': 0.709865927696228, 'Q5': 0.4288080036640167}},
            {'SumQE': {'Q1': 0.6729671359062195, 'Q2': 0.9227149486541748, 'Q3': 0.38279804587364197, 'Q4': 0.5190898180007935, 'Q5': 0.16473910212516785}}
        ]
        super().assert_expected_output(metric, expected_output)

    def test_sum_que_order_invariant(self):
        metric = SumQE(python_binary=os.environ['SUMQE_PYTHON_BINARY'])
        self.assert_order_invariant(metric)

    def test_commandline_runs(self):
        self.assert_commandline_runs('sum-qe', ['--python_binary', f'{os.environ["SUMQE_PYTHON_BINARY"]}'])