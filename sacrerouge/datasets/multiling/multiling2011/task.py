import os
import zipfile
from collections import defaultdict
from io import BytesIO
from typing import Dict, List

from sacrerouge.io import JsonlWriter
from sacrerouge.datasets.multiling.util import LANGUAGE_CODES


def load_documents(data_path: str) -> Dict[str, Dict[str, List]]:
    documents = defaultdict(lambda: defaultdict(list))

    with zipfile.ZipFile(data_path, 'r') as zip:
        documents_zip_bytes = zip.read('PublishedCorpusFileSet/MultiLingPilot2011-SourceTextsV1.0.zip')
        with zipfile.ZipFile(BytesIO(documents_zip_bytes)) as documents_zip:
            for name in documents_zip.namelist():
                if name.startswith('SourceTexts/M'):
                    filename = os.path.basename(name)
                    key, language = filename.split('.')
                    language = language.lower()
                    instance_id = key[:4]

                    # The documents seem to use blank lines to separate paragraphs,
                    # but since we don't have a sentence tokenization tool for every
                    # language, we don't attempt to do any further preprocessing.
                    document_bytes = documents_zip.read(name)
                    text = BytesIO(document_bytes).read().decode(errors='replace')
                    lines = list(filter(None, map(lambda line: line.strip(), text.splitlines())))
                    document = {
                        'filename': filename,
                        'text': lines
                    }
                    documents[language][instance_id].append(document)
    return documents


def load_summaries(data_path: str) -> Dict[str, Dict[str, List]]:
    summaries = defaultdict(lambda: defaultdict(list))

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
                    annotator = parts[1]

                    # The summaries don't seem to have any structure, so
                    # just read in the full text.
                    lines = summaries_zip.read(name).decode().splitlines()
                    clean_lines = []
                    for line in lines:
                        line = line.strip()
                        if line:
                            clean_lines.append(line)
                    text = ' '.join(clean_lines)
                    summary = {
                        'annotator': annotator,
                        'text': text
                    }
                    summaries[language][instance_id].append(summary)
    return summaries


def save_data(documents: Dict[str, Dict[str, List]],
              summaries: Dict[str, Dict[str, List]],
              output_dir: str) -> None:
    for language in documents.keys():
        code = LANGUAGE_CODES[language]
        with JsonlWriter(f'{output_dir}/{code}.jsonl') as out:
            for instance_id in sorted(documents[language].keys()):
                these_documents = documents[language][instance_id]
                these_summaries = summaries[language][instance_id]
                out.write({
                    'instance_id': instance_id,
                    'documents': these_documents,
                    'summaries': these_summaries
                })


def setup(data_path: str, output_dir: str):
    documents = load_documents(data_path)
    summaries = load_summaries(data_path)
    save_data(documents, summaries, output_dir)
