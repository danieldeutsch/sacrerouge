import csv
import zipfile
from collections import defaultdict
from io import StringIO
from typing import Dict, List

from sacrerouge.datasets.multiling.util import LANGUAGE_CODES
from sacrerouge.io import JsonlWriter


def load_quality_annotations(zip_path: str):
    summaries = defaultdict(list)
    annotations = defaultdict(list)

    with zipfile.ZipFile(zip_path, 'r') as zip:
        contents = zip.open('v2/train/data.csv', 'r').read().decode()
        reader = csv.reader(StringIO(contents), delimiter=',')

        # The summarizer_ids are unknown, so we assign each annotation a
        # unique id so that they won't match.
        summarizer_id = 0
        for i, row in enumerate(reader):
            if i == 0:
                # Header
                continue

            summary_path, score, model_paths, source_paths = row
            if len(score) > 0:
                # If it's an empty string, the summary wasn't judged
                score = float(score)
                summary = zip.open(f'v2/train/{summary_path}').read().decode().splitlines()

                references = []
                for model_path in model_paths.split(','):
                    references.append({
                        'file_path': model_path,
                        'text': zip.open(f'v2/train/{model_path}', 'r').read().decode().splitlines()
                    })

                documents = []
                for source_path in source_paths.split(','):
                    documents.append({
                        'file_path': source_path,
                        'text': zip.open(f'v2/train/{source_path}', 'r').read().decode().splitlines()
                    })

                parts = summary_path.split('/')
                instance_id = parts[0]
                language = parts[1]
                code = LANGUAGE_CODES[language]

                summaries[code].append({
                    'instance_id': instance_id,
                    'summarizer_id': str(summarizer_id),
                    'summarizer_type': 'peer',
                    'documents': documents,
                    'summary': {'text': summary},
                    'references': references
                })
                annotations[code].append({
                    'instance_id': instance_id,
                    'summarizer_id': str(summarizer_id),
                    'summarizer_type': 'peer',
                    'metrics': {'multiling2019_score': score}
                })
                summarizer_id += 1
    return summaries, annotations


def save_data(items: List, file_path: str) -> None:
    with JsonlWriter(file_path) as out:
        for item in items:
            out.write(item)


def setup(zip_path: str, output_dir: str) -> None:
    summaries_dict, annotations_dict = load_quality_annotations(zip_path)
    for language in annotations_dict.keys():
        save_data(summaries_dict[language], f'{output_dir}/{language}/summaries.jsonl')
        save_data(annotations_dict[language], f'{output_dir}/{language}/metrics.jsonl')
