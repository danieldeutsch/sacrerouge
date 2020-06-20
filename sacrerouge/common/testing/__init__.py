FIXTURES_ROOT = 'sacrerouge/tests/fixtures'

MULTILING_DOCUMENTS = f'{FIXTURES_ROOT}/data/multiling2011/documents.jsonl'
MULTILING_SUMMARIES = f'{FIXTURES_ROOT}/data/multiling2011/summaries.jsonl'
MULTILING_METRICS = f'{FIXTURES_ROOT}/data/multiling2011/metrics.jsonl'

# Import after constants so the classes can use them
from sacrerouge.common.testing.metric_test_cases import ReferenceBasedMetricTestCase