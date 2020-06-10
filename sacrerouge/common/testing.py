from typing import List

from sacrerouge.data.types import ReferenceType, SummaryType
from sacrerouge.io import JsonlReader

FIXTURES_ROOT = 'sacrerouge/tests/fixtures'


def load_summaries(file_path: str) -> List[SummaryType]:
    fields = []
    for data in JsonlReader(file_path).read():
        fields.append(data['summary'])
    return fields


def load_references(file_path: str) -> List[ReferenceType]:
    fields = []
    for data in JsonlReader(file_path).read():
        if 'summary' in data:
            fields.append([data['summary']['text']])
        elif 'summaries' in data:
            fields.append([summary['text'] for summary in data['summaries']])
        elif 'reference' in data:
            fields.append([data['reference']['text']])
        elif 'references' in data:
            fields.append([reference['text'] for reference in data['references']])
    return fields
