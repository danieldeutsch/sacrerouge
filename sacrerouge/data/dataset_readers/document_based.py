import logging
from typing import Any, List, Union

from sacrerouge.data import EvalInstance
from sacrerouge.data.dataset_readers import DatasetReader
from sacrerouge.data.fields import DocumentsField, Fields, SummaryField
from sacrerouge.io import JsonlReader

logger = logging.getLogger(__name__)


def flatten_document(document: Any) -> Union[List[str], str]:
    """"
    If the document is a single string, nothing is changed. If the document is a nested list of strings,
    it will be flattened to be one list of strings without any nesting.
    """
    if isinstance(document, str):
        return document
    flat = []
    for item in document:
        if isinstance(item, str):
            flat.append(item)
        else:
            flat.extend(flatten_document(item))
    return flat


def flatten_documents(documents: List[Any]) -> List[Union[List[str], str]]:
    return [flatten_document(document) for document in documents]


@DatasetReader.register('document-based')
class DocumentBasedDatasetReader(DatasetReader):
    def read(self, input_jsonl: str) -> List[EvalInstance]:
        logger.info(f'Loading evaluation instances from {input_jsonl}')
        instances = []
        with JsonlReader(input_jsonl) as f:
            for data in f:
                fields = {}
                fields['summary'] = SummaryField(data['summary']['text'])

                if 'document' in data:
                    fields['documents'] = DocumentsField([data['document']['text']])
                else:
                    fields['documents'] = DocumentsField([document['text'] for document in data['documents']])
                fields = Fields(fields)

                instance = EvalInstance(
                    data['instance_id'],
                    data['summarizer_id'],
                    data['summarizer_type'],
                    fields
                )
                instances.append(instance)

            logger.info(f'Loaded {len(instances)} instances')
            return instances


@DatasetReader.register('split-document-based')
class SplitDocumentBasedDatasetReader(DatasetReader):
    def read(self, documents_jsonl: str, summaries_jsonl) -> List[EvalInstance]:
        logger.info(f'Loading documents from {documents_jsonl}')
        documents_dict = {}
        with JsonlReader(documents_jsonl) as f:
            for data in f:
                instance_id = data['instance_id']
                if 'document' in data:
                    documents = [data['document']['text']]
                else:
                    documents = [document['text'] for document in data['documents']]
                documents = flatten_documents(documents)
                documents_dict[instance_id] = DocumentsField(documents)
        logger.info(f'Loaded {len(documents_dict)} document sets')

        logger.info(f'Loading summaries from {summaries_jsonl}')
        instances = []
        with JsonlReader(summaries_jsonl) as f:
            for data in f:
                fields = {}
                fields['summary'] = SummaryField(data['summary']['text'])

                instance_id = data['instance_id']
                fields['documents'] = documents_dict[instance_id]
                fields = Fields(fields)

                instance = EvalInstance(
                    data['instance_id'],
                    data['summarizer_id'],
                    data['summarizer_type'],
                    fields
                )
                instances.append(instance)
        logger.info(f'Loaded {len(instances)} instances')
        return instances
