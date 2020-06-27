import tarfile
from collections import defaultdict
from nltk.tokenize import sent_tokenize

from sacrerouge.io import JsonlWriter


def load_documents(tar_path: str):
    documents = defaultdict(dict)
    with tarfile.open(tar_path, 'r') as tar:
        for member in tar.getmembers():
            if member.name.startswith('2017_test_data/body/text') and member.name.endswith('.txt'):
                if 'simple' in member.name:
                    # Seems to be a dummy language
                    continue
                language = member.name[25:27]
                instance_id = member.name[28:60]
                text = tar.extractfile(member).read().decode().splitlines()
                if language == 'en':
                    text = [sent_tokenize(paragraph) for paragraph in text]
                document = {
                    'filename': instance_id,
                    'text': text
                }
                documents[language][instance_id] = document
    return documents


def load_summaries(eval_path: str):
    summaries = defaultdict(dict)
    with tarfile.open(eval_path, 'r') as tar:
        for member in tar.getmembers():
            if member.name.startswith('Evaluation/2017_summaries/') and member.name.endswith('.txt'):
                if 'simple' in member.name:
                    # Seems to be a dummy language
                    continue
                path = member.name.split('/')
                language_code = path[2]
                instance_id = path[3][:32]
                text = tar.extractfile(member).read().decode().splitlines()
                if language_code == 'en':
                    text = [sent_tokenize(paragraph) for paragraph in text]
                summaries[language_code][instance_id] = {
                    'text': text
                }
    return summaries


def save_data(documents, summaries, output_dir: str):
    for language in documents.keys():
        with JsonlWriter(f'{output_dir}/{language}.jsonl') as out:
            for instance_id in sorted(documents[language].keys()):
                out.write({
                    'instance_id': instance_id,
                    'document': documents[language][instance_id],
                    'summary': summaries[language][instance_id]
                })


def setup(data_path: str, eval_path: str, output_dir: str):
    documents = load_documents(data_path)
    summaries = load_summaries(eval_path)
    save_data(documents, summaries, output_dir)
