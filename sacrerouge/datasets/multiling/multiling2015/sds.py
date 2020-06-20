import tarfile
from collections import defaultdict
from nltk.tokenize import sent_tokenize

from sacrerouge.io import JsonlWriter


def load_documents(tar_path: str):
    documents = defaultdict(dict)
    with tarfile.open(tar_path, 'r') as tar:
        for member in tar.getmembers():
            if member.name.startswith('multilingMss2015Eval/body/text') and member.name.endswith('.txt'):
                language = member.name[31:33]
                instance_id = member.name[34:66]
                text = tar.extractfile(member).read().decode().splitlines()
                if language == 'en':
                    text = [sent_tokenize(paragraph) for paragraph in text]
                document = {
                    'filename': instance_id,
                    'text': text
                }
                documents[language][instance_id] = document
    return documents


def load_summaries(tar_path: str):
    summaries = defaultdict(dict)
    with tarfile.open(tar_path, 'r') as tar:
        for member in tar.getmembers():
            if member.name.startswith('multilingMss2015Eval/summary') and member.name.endswith('.txt'):
                language = member.name[29:31]
                instance_id = member.name[32:64]
                text = tar.extractfile(member).read().decode().splitlines()
                if language == 'en':
                    text = [sentence for paragraph in text for sentence in sent_tokenize(paragraph)]
                summary = {
                    'text': text
                }
                summaries[language][instance_id] = summary
    return summaries


def save_data(documents, summaries, output_dir):
    for language in documents.keys():
        with JsonlWriter(f'{output_dir}/{language}.jsonl') as out:
            for filename, document in documents[language].items():
                summary = summaries[language][filename]
                out.write({
                    'instance_id': filename,
                    'document': document,
                    'summary': summary
                })


def setup(tar_path: str, output_dir: str):
    documents = load_documents(tar_path)
    summaries = load_summaries(tar_path)
    save_data(documents, summaries, output_dir)