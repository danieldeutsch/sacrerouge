import zipfile
from collections import defaultdict

from sacrerouge.io import JsonlWriter
from sacrerouge.datasets.multiling.multiling2013.util import LANGUAGE_CODES


def load_documents(documents_zip: str):
    documents = defaultdict(lambda: defaultdict(list))

    with zipfile.ZipFile(documents_zip) as zip:
        for file_path in zip.namelist():
            if file_path.startswith('SourceTextsV2b/M'):
                filename = file_path[15:]
                # The filenames are like "M1047.english" where the cluster is "M104", it is the 7th document, and an English document
                instance_id, language = filename.split('.')
                instance_id = instance_id[:-1]
                language_code = LANGUAGE_CODES[language]

                # Contents are the plain text of the document. Blank lines seem to separate paragraphs.
                # No sentence breaking done
                contents = zip.open(file_path, 'r').read().decode()
                text = list(filter(None, [line.strip() for line in contents.splitlines()]))

                document = {
                    'filename': filename,
                    'text': text
                }
                documents[language_code][instance_id].append(document)
    return documents


def load_summaries(summaries_zip: str):
    summaries = defaultdict(lambda: defaultdict(list))
    with zipfile.ZipFile(summaries_zip) as zip:
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
                summaries[language_code][instance_id].append({
                    'annotator': annotator,
                    'text': text
                })
    return summaries


def save_data(documents, summaries, output_dir) -> None:
    for language in documents.keys():
        with JsonlWriter(f'{output_dir}/{language}.jsonl') as out:
            for instance_id in sorted(documents[language].keys()):
                lang_documents = documents[language][instance_id]
                lang_summaries = summaries[language][instance_id]
                out.write({
                    'instance_id': instance_id,
                    'documents': lang_documents,
                    'summaries': lang_summaries
                })


def setup(documents_zip: str, summaries_zip: str, output_dir: str) -> None:
    documents = load_documents(documents_zip)
    summaries = load_summaries(summaries_zip)
    save_data(documents, summaries, output_dir)
