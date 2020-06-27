import zipfile
from collections import defaultdict

from sacrerouge.io import JsonlWriter
from sacrerouge.datasets.multiling.util import LANGUAGE_CODES


def load_training_data(train_zip: str):
    documents = defaultdict(lambda: defaultdict(list))
    summaries = defaultdict(lambda: defaultdict(list))
    with zipfile.ZipFile(train_zip, 'r') as zip:
        for file_path in zip.namelist():
            if file_path.endswith('.250'):
                path = file_path.split('/')
                language_code = LANGUAGE_CODES[path[1]]
                filename = path[3]
                parts = filename.split('.')
                instance_id = parts[0]
                annotator = parts[1]

                contents = zip.open(file_path, 'r').read().decode()
                text = list(filter(None, [line.strip() for line in contents.splitlines()]))
                summaries[language_code][instance_id].append({
                    'annotator': annotator,
                    'text': text
                })

            elif '/M00' in file_path:
                path = file_path.split('/')
                language_code = LANGUAGE_CODES[path[1]]
                filename = path[3]
                parts = filename.split('.')
                instance_id = parts[0][:-1]

                contents = zip.open(file_path, 'r').read().decode()
                text = list(filter(None, [line.strip() for line in contents.splitlines()]))
                documents[language_code][instance_id].append({
                    'filename': filename,
                    'text': text
                })

    return documents, summaries


def load_testing_data(test_zip: str):
    documents = defaultdict(lambda: defaultdict(list))
    with zipfile.ZipFile(test_zip, 'r') as zip:
        for file_path in zip.namelist():
            if '/M00' in file_path:
                path = file_path.split('/')
                language_code = LANGUAGE_CODES[path[1]]
                filename = path[2]
                parts = filename.split('.')
                instance_id = parts[0][:-1]

                if instance_id in ['M001', 'M002', 'M003']:
                    # According to the Wiki, these are not taken into account during evaluation
                    # because these are the training topics
                    # http://multiling.iit.demokritos.gr/pages/view/1540/task-mms-multi-document-summarization-data-and-information
                    continue

                contents = zip.open(file_path, 'r').read().decode()
                text = list(filter(None, [line.strip() for line in contents.splitlines()]))
                documents[language_code][instance_id].append({
                    'filename': filename,
                    'text': text
                })
    return documents


def save_data(train_documents, train_summaries, test_documents, output_dir):
    for language in train_documents.keys():
        with JsonlWriter(f'{output_dir}/{language}.train.jsonl') as out:
            for instance_id in sorted(train_documents[language].keys()):
                out.write({
                    'instance_id': instance_id,
                    'documents': train_documents[language][instance_id],
                    'summaries': train_summaries[language][instance_id]
                })

        with JsonlWriter(f'{output_dir}/{language}.test.jsonl') as out:
            for instance_id in sorted(test_documents[language].keys()):
                out.write({
                    'instance_id': instance_id,
                    'documents': test_documents[language][instance_id]
                })


def setup(train_zip: str, test_zip: str, output_dir: str):
    train_documents, train_summaries = load_training_data(train_zip)
    test_documents = load_testing_data(test_zip)
    save_data(train_documents, train_summaries, test_documents, output_dir)