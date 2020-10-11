import unittest

from sacrerouge.data.dataset_readers.document_based import flatten_document


class TestDocumentBasedReader(unittest.TestCase):
    def test_flatten_document(self):
        document = [
            'A',
            ['B', ['C', 'D', ['E']]],
            ['F']
        ]
        assert flatten_document(document) == ['A', 'B', 'C', 'D', 'E', 'F']
