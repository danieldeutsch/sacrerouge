from collections import defaultdict
from typing import Dict, List

from sacrerouge.data import Metrics, MetricsDict
from sacrerouge.data.types import ReferenceType, SummaryType
from sacrerouge.io import JsonlReader


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


def load_metrics_dicts(file_path: str) -> Dict[str, Dict[str, MetricsDict]]:
    metrics_dicts = defaultdict(dict)
    with JsonlReader(file_path, Metrics) as f:
        for instance in f:
            metrics_dicts[instance.instance_id][instance.summarizer_id] = instance.metrics
    return metrics_dicts