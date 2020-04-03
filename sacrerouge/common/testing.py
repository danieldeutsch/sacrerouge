from typing import List

from sacrerouge.data.fields import ReferencesField, SummaryField
from sacrerouge.io import JsonlReader

FIXTURES_ROOT = 'sacrerouge/tests/fixtures'


def load_summaries(file_path: str) -> List[SummaryField]:
    fields = []
    for data in JsonlReader(file_path).read():
        fields.append(SummaryField(data['summary']))
    return fields


def load_references(file_path: str) -> List[ReferencesField]:
    fields = []
    for data in JsonlReader(file_path).read():
        if 'summary' in data:
            fields.append(ReferencesField([data['summary']]))
        elif 'summaries' in data:
            fields.append(ReferencesField(data['summaries']))
        elif 'reference' in data:
            fields.append(ReferencesField([data['reference']]))
        elif 'references' in data:
            fields.append(ReferencesField(data['references']))
    return fields
