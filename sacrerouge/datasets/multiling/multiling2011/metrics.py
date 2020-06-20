import os
import zipfile
from collections import defaultdict
from io import BytesIO
from nltk import sent_tokenize
from typing import Any, Dict

from sacrerouge.data import Metrics, MetricsDict
from sacrerouge.io import JsonlWriter
from sacrerouge.datasets.multiling.multiling2011.util import LANGUAGE_CODES


FILE_ID_TO_INSTANCE_ID = {
    1: 'M002',
    2: 'M003',
    3: 'M001',
    4: 'M000',
    5: 'M007',
    6: 'M005',
    7: 'M004',
    8: 'M006',
    9: 'M008',
    10: 'M009'
}


def load_reference_summaries(data_path: str,
                             summaries: Dict[str, Dict[str, Dict[str, Any]]]):
    with zipfile.ZipFile(data_path, 'r') as zip:
        summaries_zip_bytes = zip.read('PublishedCorpusFileSet/MultiLingPilot2011-ModelSummaries.zip')
        with zipfile.ZipFile(BytesIO(summaries_zip_bytes)) as summaries_zip:
            for name in summaries_zip.namelist():
                if name.endswith('.250'):
                    path = name.split('/')
                    language = path[0].lower()
                    filename = path[1]
                    parts = filename.split('.')
                    instance_id = parts[0][:4]
                    summarizer_id = parts[1]

                    # The summaries don't seem to have any structure, so
                    # just read in the full text.
                    lines = summaries_zip.read(name).decode().splitlines()
                    clean_lines = []
                    for line in lines:
                        line = line.strip()
                        if line:
                            clean_lines.append(line)
                    text = ' '.join(clean_lines)
                    # Sentence tokenize English only
                    if language == 'english':
                        text = sent_tokenize(text)

                    summary = {
                        'summarizer_id': summarizer_id,
                        'summarizer_type': 'reference',
                        'text': text
                    }
                    summaries[language][instance_id][summarizer_id] = summary


def load_peer_summaries(data_path: str,
                        summaries: Dict[str, Dict[str, Dict[str, Any]]]):
    with zipfile.ZipFile(data_path, 'r') as zip:
        summaries_zip_bytes = zip.read('PublishedCorpusFileSet/MultiLingPilot2011-PeerSummaries.zip')
        with zipfile.ZipFile(BytesIO(summaries_zip_bytes)) as summaries_zip:
            for name in summaries_zip.namelist():
                filename = os.path.basename(name)
                if filename.startswith('M00'):
                    path = name.split('/')
                    summarizer_id = path[1][2:]
                    language = path[2].lower()
                    instance_id = path[3][:4]

                    # Lines are roughly sentences (not always), so we keep them intact
                    lines = summaries_zip.read(name).decode().splitlines()
                    clean_lines = []
                    for line in lines:
                        line = line.strip()
                        if line:
                            clean_lines.append(line)
                    lines = clean_lines

                    summary = {
                        'summarizer_id': summarizer_id,
                        'summarizer_type': 'peer',
                        'text': lines
                    }
                    summaries[language][instance_id][summarizer_id] = summary


def load_autosummeng_output(data_path: str, metrics):
    with zipfile.ZipFile(data_path, 'r') as zip:
        eval_zip_bytes = zip.read('PublishedCorpusFileSet/MultiLingPilot2011-EvaluationResults.zip')
        with zipfile.ZipFile(BytesIO(eval_zip_bytes)) as eval_zip:
            for name in eval_zip.namelist():
                if name.startswith('PublishedEvaluation/AutomaticEvaluation/AutoSummENG/Detailed/') and name.endswith('.csv'):
                    filename = os.path.basename(name)
                    # strip "Detailed.csv" off the end to get the language name
                    language = filename[:-12]

                    lines = eval_zip.read(name).decode().splitlines()
                    for line in lines[1:]:
                        columns = line.split()
                        instance_id = columns[0]
                        summarizer_id = columns[1][2:]
                        # There are only scores for peers, so no jackknifing
                        metrics[language][instance_id][summarizer_id]['MeMoG'] = float(columns[3])


def load_rouge_output(data_path: str, metrics):
    with zipfile.ZipFile(data_path, 'r') as zip:
        eval_zip_bytes = zip.read('PublishedCorpusFileSet/MultiLingPilot2011-EvaluationResults.zip')
        with zipfile.ZipFile(BytesIO(eval_zip_bytes)) as eval_zip:
            for name in eval_zip.namelist():
                if name.startswith('PublishedEvaluation/AutomaticEvaluation/ROUGE/Detailed/') and name.endswith('.txt'):
                    filename = os.path.basename(name)
                    # strip "Detailed.txt" off the end to get the language name
                    language = filename[:-12]

                    lines = eval_zip.read(name).decode().splitlines()
                    for line in lines:
                        columns = line.split()
                        if len(columns) == 7 and columns[2] == 'Eval':
                            summarizer_id = columns[0]
                            rouge_metric = columns[1].lower()
                            # The file_id and summarizer_id appear like "5.ID3". The file_id
                            # seems to have no correspondence with the instance_id. We found
                            # this mapping by computing the rouge score ourselves and then
                            # finding the mapping
                            file_id = int(columns[3].split('.')[0])
                            instance_id = FILE_ID_TO_INSTANCE_ID[file_id]
                            summarizer_id = columns[3].split('.')[1][2:]

                            recall = float(columns[4][2:]) * 100
                            precision = float(columns[5][2:]) * 100
                            f1 = float(columns[6][2:]) * 100
                            # Only peers evaluated, no jackknifing
                            metrics[language][instance_id][summarizer_id][rouge_metric] = {
                                'recall': recall,
                                'precision': precision,
                                'f1': f1
                            }


def load_manual_output(data_path: str, metrics):
    with zipfile.ZipFile(data_path, 'r') as zip:
        eval_zip_bytes = zip.read('PublishedCorpusFileSet/MultiLingPilot2011-EvaluationResults.zip')
        with zipfile.ZipFile(BytesIO(eval_zip_bytes)) as eval_zip:
            for name in eval_zip.namelist():
                if name.startswith('PublishedEvaluation/HumanEvaluation/') and name.endswith('.csv'):
                    filename = os.path.basename(name)
                    # strip "Grades.csv" off the end to get the language name
                    language = filename[:-10]

                    lines = eval_zip.read(name).decode().splitlines()
                    for line in lines[1:]:
                        columns = line.split()
                        # Strip the quotes from the instance and summarizer
                        instance_id = columns[0][1:-1]
                        summarizer_id = columns[1][3:-1]

                        if 'grade' not in metrics[language][instance_id][summarizer_id]:
                            metrics[language][instance_id][summarizer_id]['grade'] = []
                        if 'length_aware_grade' not in metrics[language][instance_id][summarizer_id]:
                            metrics[language][instance_id][summarizer_id]['length_aware_grade'] = []

                        metrics[language][instance_id][summarizer_id]['grade'].append(int(columns[4]))
                        metrics[language][instance_id][summarizer_id]['length_aware_grade'].append(float(columns[6]))


def get_references(summaries, instance_id, summarizer_id):
    summarizer_ids = list(summaries[instance_id].keys())
    reference_ids = list(filter(lambda sid: sid.isalpha(), summarizer_ids))

    references = []
    for reference_id in reference_ids:
        if summarizer_id == reference_id:
            continue
        references.append(summaries[instance_id][reference_id])
    return references


def save_data(summaries, metrics, output_dir: str):
    for language in summaries.keys():
        code = LANGUAGE_CODES[language]

        with JsonlWriter(f'{output_dir}/{code}.summaries.jsonl') as out_summaries:
            with JsonlWriter(f'{output_dir}/{code}.metrics.jsonl') as out_metrics:
                for instance_id in sorted(summaries[language].keys()):
                    for summarizer_id in sorted(summaries[language][instance_id].keys()):
                        summary = summaries[language][instance_id][summarizer_id]
                        instance_metrics = metrics[language][instance_id][summarizer_id]
                        references = get_references(summaries[language], instance_id, summarizer_id)

                        out_summaries.write({
                            'instance_id': instance_id,
                            'summarizer_id': summarizer_id,
                            'summarizer_type': summary['summarizer_type'],
                            'summary': summary,
                            'references': references
                        })
                        out_metrics.write(Metrics(instance_id, summarizer_id, summary['summarizer_type'], instance_metrics))


def setup(data_path: str, output_dir: str):
    summaries = defaultdict(lambda: defaultdict(dict))
    load_reference_summaries(data_path, summaries)
    load_peer_summaries(data_path, summaries)

    metrics = defaultdict(lambda: defaultdict(MetricsDict))
    load_autosummeng_output(data_path, metrics)
    load_rouge_output(data_path, metrics)
    load_manual_output(data_path, metrics)
    save_data(summaries, metrics, output_dir)
