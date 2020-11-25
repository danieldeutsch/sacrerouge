import spacy

from sacrerouge.common.testing import FIXTURES_ROOT
from sacrerouge.common.testing.metric_test_cases import ReferenceBasedMetricTestCase
from sacrerouge.common.testing.util import sacrerouge_command_exists
from sacrerouge.io import JsonlReader
from sacrerouge.metrics import DecomposedRouge


class TestDecomposedRouge(ReferenceBasedMetricTestCase):
    def test_spacy_model_version(self):
        # These results rely on having spacy en_core_web_sm version 2.3.1 installed
        nlp = spacy.load('en_core_web_sm')
        assert nlp.meta['version'] == '2.3.1'

    def test_regression(self):
        # This is a regression test, not necessarily a test for correctness. The expected output
        # is really long, so we saved it in a file
        metric = DecomposedRouge()
        expected_output = JsonlReader(f'{FIXTURES_ROOT}/data/decomposed-rouge/expected-output.jsonl').read()
        super().assert_expected_output(metric, expected_output)

    def test_order_invariant(self):
        metric = DecomposedRouge()
        self.assert_order_invariant(metric)

    def test_command_exists(self):
        assert sacrerouge_command_exists(['decomposed-rouge'])

    def test_setup_command_exists(self):
        assert sacrerouge_command_exists(['setup-metric', 'decomposed-rouge'])