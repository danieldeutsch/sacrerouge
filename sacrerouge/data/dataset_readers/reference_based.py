from typing import List

from sacrerouge.data import EvalInstance
from sacrerouge.data.dataset_readers import DatasetReader
from sacrerouge.data.fields import ReferencesField, Fields, SummaryField
from sacrerouge.io import JsonlReader


@DatasetReader.register('reference-based')
class ReferenceBasedDatasetReader(DatasetReader):
    def read(self, input_jsonl: str) -> List[EvalInstance]:
        instances = []
        with JsonlReader(input_jsonl) as f:
            for data in f:
                summary = SummaryField(data['summary']['text'])

                if 'reference' in data:
                    references = ReferencesField([data['reference']['text']])
                else:
                    references = ReferencesField([reference['text'] for reference in data['references']])
                fields = Fields({'references': references})

                instance = EvalInstance(
                    data['instance_id'],
                    data['summarizer_id'],
                    data['summarizer_type'],
                    summary,
                    fields
                )
                instances.append(instance)
            return instances
