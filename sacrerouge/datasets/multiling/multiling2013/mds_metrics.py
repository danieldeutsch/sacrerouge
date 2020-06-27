import csv
import jsons
import zipfile
from collections import defaultdict

from sacrerouge.data import Metrics, MetricsDict
from sacrerouge.io import JsonlWriter
from sacrerouge.datasets.multiling.util import LANGUAGE_CODES


def load_model_summaries(summaries_zip: str):
    summaries = defaultdict(lambda: defaultdict(dict))
    with zipfile.ZipFile(summaries_zip, 'r') as zip:
        for file_path in zip.namelist():
            if file_path.endswith('.250'):
                path = file_path.split('/')
                language_code = LANGUAGE_CODES[path[1]]
                parts = path[2].split('.')
                instance_id = parts[0]
                annotator = parts[1]

                # The summaries don't seem to have any structure, so
                # just read in the full text.
                contents = zip.open(file_path, 'r').read().decode()
                text = list(filter(None, [line.strip() for line in contents.splitlines()]))
                summaries[language_code][instance_id][annotator] = {
                    'summarizer_id': annotator,
                    'summarizer_type': 'reference',
                    'text': text
                }
    return summaries


def load_peer_summaries(summaries_zip: str):
    summaries = defaultdict(lambda: defaultdict(dict))
    with zipfile.ZipFile(summaries_zip, 'r') as zip:
        for file_path in zip.namelist():
            if file_path.endswith('.250'):
                path = file_path.split('/')
                summarizer_id = path[1]
                language_code = LANGUAGE_CODES[path[2]]

                parts = path[3].split('.')
                instance_id = parts[0]

                contents = zip.open(file_path, 'r').read().decode()
                text = list(filter(None, [line.strip() for line in contents.splitlines()]))

                summaries[language_code][instance_id][summarizer_id] = {
                    'summarizer_id': summarizer_id,
                    'summarizer_type': 'reference',
                    'text': text
                }
    return summaries


def load_metrics(grades_zip: str):
    metrics = defaultdict(lambda: defaultdict(lambda: defaultdict(MetricsDict)))
    with zipfile.ZipFile(grades_zip, 'r') as zip:
        for file_path in zip.namelist():
            if file_path.endswith('.csv'):
                reader = csv.reader(zip.open(file_path, 'r').read().decode().splitlines(), delimiter='\t')
                for i, line in enumerate(reader):
                    if i == 0:
                        continue  # header
                    instance_id, summarizer_id, language, _, _, overall_responsiveness = line
                    language_code = LANGUAGE_CODES[language]
                    overall_responsiveness = float(overall_responsiveness)
                    if 'overall_responsiveness' not in metrics[language_code][instance_id][summarizer_id]:
                        metrics[language_code][instance_id][summarizer_id] = MetricsDict({'overall_responsiveness': []})
                    metrics[language_code][instance_id][summarizer_id]['overall_responsiveness'].append(overall_responsiveness)
    return metrics


def save_data(model_summaries, peer_summaries, metrics, output_dir):
    for language in model_summaries.keys():
        with JsonlWriter(f'{output_dir}/{language}.summaries.jsonl') as out_summaries:
            if language in metrics:
                out_metrics = open(f'{output_dir}/{language}.metrics.jsonl', 'w')
            else:
                out_metrics = None

            for instance_id in sorted(model_summaries[language].keys()):
                references = list(model_summaries[language][instance_id][key] for key in sorted(model_summaries[language][instance_id].keys()))
                for summarizer_id in sorted(peer_summaries[language][instance_id].keys()):
                    summary = peer_summaries[language][instance_id][summarizer_id]
                    out_summaries.write({
                        'instance_id': instance_id,
                        'summarizer_id': summarizer_id,
                        'summarizer_type': 'peer',
                        'summary': summary,
                        'references': references
                    })
                    if out_metrics is not None:
                        instance_metrics = metrics[language][instance_id][summarizer_id]
                        out_metrics.write(jsons.dumps(Metrics(instance_id, summarizer_id, 'peer', instance_metrics)) + '\n')

                for i, reference in enumerate(references):
                    summarizer_id = reference['summarizer_id']
                    out_summaries.write({
                        'instance_id': instance_id,
                        'summarizer_id': summarizer_id,
                        'summarizer_type': 'reference',
                        'summary': reference,
                        'references': references[:i] + references[i + 1:]
                    })
                    if out_metrics is not None:
                        instance_metrics = metrics[language][instance_id][summarizer_id]
                        out_metrics.write(jsons.dumps(Metrics(instance_id, summarizer_id, 'reference', instance_metrics)) + '\n')

            if out_metrics is not None:
                out_metrics.close()


def setup(model_summaries_zip: str, peer_summaries_zip: str, grades_zip: str, output_dir: str) -> None:
    model_summaries = load_model_summaries(model_summaries_zip)
    peer_summaries = load_peer_summaries(peer_summaries_zip)
    metrics = load_metrics(grades_zip)
    save_data(model_summaries, peer_summaries, metrics, output_dir)