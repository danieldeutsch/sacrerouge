import lxml.html
import re
import tarfile
from collections import defaultdict
from io import BytesIO
from nltk.tokenize import sent_tokenize
from typing import Dict, List, Tuple

from sacrerouge.io import JsonlWriter


# There are errors in the extractive MDS that have the
# incorrect file IDs
doc_id_overrides = {
    'AP890729-0155': 'AP880729-0155',
    'SJMN91-06048': 'SJMN91-06165048',
    'AP880428-\r\n0041': 'AP880428-0041',
    'AP880818-\r\n0088': 'AP880818-0088'
}


def load_extractive_document(tar, member) -> List[str]:
    html = tar.extractfile(member).read().decode()
    tree = lxml.html.document_fromstring(html)
    sentences = []
    for node in tree.xpath('//s'):
        num = int(node.get('num'))
        assert num == len(sentences) + 1
        text = node.text_content().strip()
        sentences.append(text)
    return sentences


def load_abstractive_document(tar, member) -> List[str]:
    html = tar.extractfile(member).read().decode()
    tree = lxml.html.document_fromstring(html)
    sentences = []
    for node in tree.xpath('//text//s'):
        text = node.text_content().strip()
        sentences.append(text)
    assert len(sentences) > 0, member.name
    return sentences


def load_documents(documents_tar_path: str) -> Tuple[Dict[List, str], Dict[str, List[str]]]:
    cluster_to_documents = defaultdict(list)
    abs_documents = {}
    ext_documents = {}

    with tarfile.open(documents_tar_path, 'r') as tar:
        inner_tar_bytes = tar.extractfile('DUC2002_Summarization_Documents/duc2002testdocswithsentences.tar.gz').read()
        with tarfile.open(fileobj=BytesIO(inner_tar_bytes)) as inner_tar:
            for member in inner_tar.getmembers():
                if member.isfile():
                    path = member.name.split('/')
                    cluster = path[2][:-1]
                    filename = path[3][:-2]

                    abs_sentences = load_abstractive_document(inner_tar, member)
                    ext_sentences = load_extractive_document(inner_tar, member)

                    abs_document = {'filename': filename, 'text': abs_sentences}
                    ext_document = {'filename': filename, 'text': ext_sentences}

                    cluster_to_documents[cluster].append(filename)
                    abs_documents[filename] = abs_document
                    ext_documents[filename] = ext_document

    return cluster_to_documents, abs_documents, ext_documents


def load_sds_summaries(summaries_tar: str) -> Dict[str, List[List[str]]]:
    summaries = defaultdict(list)
    with tarfile.open(summaries_tar, 'r') as tar:
        for member in tar.getmembers():
            if member.isfile():
                if member.name.startswith('./extracts_abstracts/d'):
                    path = member.name.split('/')
                    filename = path[-1]
                    if filename == 'perdocs':
                        html = tar.extractfile(member).read().decode()
                        tree = lxml.html.document_fromstring(html)
                        for node in tree.xpath('body/sum'):
                            doc = node.attrib['docref']
                            text = node.text_content().strip()
                            text = re.sub('\s+', ' ', text)
                            sentences = sent_tokenize(text)
                            annotator = path[2][-1].upper()
                            summary = {
                                'annotator': annotator,
                                'text': sentences
                            }
                            if doc in summaries and sentences in summaries[doc]:
                                print(f'Document {doc} has a duplicate SDS. Skipping')
                            summaries[doc].append(summary)
    return summaries


def load_mds_abstractive_summaries(summaries_tar: str) -> Dict[str, Dict[int, List[List[str]]]]:
    summaries = defaultdict(lambda: defaultdict(list))
    with tarfile.open(summaries_tar, 'r') as tar:
        for member in tar.getmembers():
            if member.isfile():
                if member.name.startswith('./extracts_abstracts/d'):
                    path = member.name.split('/')
                    cluster = path[2][:-2]
                    filename = path[-1]
                    if filename in ['10', '50', '100', '200']:
                        length = int(filename)
                        html = tar.extractfile(member).read().decode()
                        tree = lxml.html.document_fromstring(html)
                        text = tree.xpath('body/sum')[0].text_content().strip()
                        text = re.sub('\s+', ' ', text)
                        sentences = sent_tokenize(text)
                        annotator = path[2][-1].upper()
                        summary = {
                            'annotator': annotator,
                            'text': sentences
                        }
                        if sentences not in summaries[cluster][length]:
                            summaries[cluster][length].append(summary)
                        else:
                            print(f'Duplicate summary of length {length} found for cluster {cluster}')
    return summaries


def load_mds_extractive_summaries(summaries_tar: str) -> Dict[str, Dict[int, List[List[str]]]]:
    summaries = defaultdict(lambda: defaultdict(list))
    with tarfile.open(summaries_tar, 'r') as tar:
        for member in tar.getmembers():
            if member.isfile():
                if member.name.startswith('./extracts_abstracts/d'):
                    path = member.name.split('/')
                    cluster = path[2][:-2]
                    filename = path[-1]
                    if filename in ['200e', '400e']:
                        length = int(filename[:-1])
                        html = tar.extractfile(member).read().decode()
                        # There is a typo in this particular file where the closing
                        # tag is actually an opening tag, and it messes up the parse
                        if member.name.endswith('d118if/200e'):
                            html = html.replace('of <s>', 'of </s>')
                        tree = lxml.html.document_fromstring(html)
                        labels = []
                        for node in tree.xpath('//s'):
                            doc = node.get('docid')
                            num = int(node.get('num'))
                            index = num - 1
                            labels.append((doc, index))

                        annotator = path[2][-1].upper()
                        summary = {
                            'annotator': annotator,
                            'labels': labels
                        }

                        if labels in summaries[cluster][length]:
                            print(f'Cluster {cluster} has duplicate extractive summaries of length {length}')
                        else:
                            summaries[cluster][length].append(summary)
    return summaries


def save_sds_data(documents: Dict[str, List[str]],
                  summaries: Dict[str, List[List[str]]],
                  file_path: str) -> None:
    with JsonlWriter(file_path) as out:
        for doc_id, document in documents.items():
            doc_summaries = summaries[doc_id]
            data = {
                'instance_id': doc_id,
                'document': document,
                'summaries': doc_summaries
            }
            out.write(data)


def save_mds_abstractive_data(cluster_to_documents: Dict[str, List[str]],
                              documents: Dict[str, List[str]],
                              summaries: Dict[str, Dict[int, List[List[str]]]],
                              length: int,
                              file_path: str) -> None:
    with JsonlWriter(file_path) as out:
        for cluster_id in sorted(cluster_to_documents.keys()):
            doc_ids = cluster_to_documents[cluster_id]
            cluster_docs = [documents[doc_id] for doc_id in doc_ids]
            cluster_summaries = summaries[cluster_id][length]
            data = {
                'instance_id': cluster_id,
                'documents': cluster_docs,
                'summaries': cluster_summaries
            }
            out.write(data)


def save_mds_extractive_data(cluster_to_documents: Dict[str, List[str]],
                             documents: Dict[str, List[str]],
                             summaries: Dict[str, Dict[int, List[List[Tuple[str, int]]]]],
                             length: int,
                             file_path: str) -> None:
    with JsonlWriter(file_path) as out:
        for cluster_id in sorted(cluster_to_documents.keys()):
            doc_ids = cluster_to_documents[cluster_id]
            doc_id_to_index = {doc_id: i for i, doc_id in enumerate(doc_ids)}

            cluster_docs = [documents[doc_id] for doc_id in doc_ids]
            cluster_summaries = []
            for summary in summaries[cluster_id][length]:
                new_labels = []
                for doc_id, index in summary['labels']:
                    if doc_id in doc_id_overrides:
                        doc_id = doc_id_overrides[doc_id]
                    new_labels.append({
                        'doc_index': doc_id_to_index[doc_id],
                        'sent_index': index
                    })

                cluster_summaries.append({
                    'annotator': summary['annotator'],
                    'labels': new_labels
                })

            data = {
                'instance_id': cluster_id,
                'documents': cluster_docs,
                'summaries': cluster_summaries
            }
            out.write(data)


def setup(data_root: str, output_dir: str) -> None:
    documents_tar = f'{data_root}/from-nist/DUC2002_Summarization_Documents.tgz'
    extracts_and_abstracts_tar = f'{data_root}/scrapes/duc.nist.gov/past_duc/duc2002/data/test/summaries/duc2002extractsandabstracts.tar.gz'
    main(documents_tar, extracts_and_abstracts_tar, output_dir)


def main(documents_tar, extracts_and_abstracts_tar, output_dir):
    cluster_to_documents, abs_documents, ext_documents = load_documents(documents_tar)
    sds_summaries = load_sds_summaries(extracts_and_abstracts_tar)
    mds_abs_summaries = load_mds_abstractive_summaries(extracts_and_abstracts_tar)
    mds_ext_summaries = load_mds_extractive_summaries(extracts_and_abstracts_tar)

    save_sds_data(abs_documents, sds_summaries, f'{output_dir}/task1.jsonl')

    save_mds_abstractive_data(cluster_to_documents, abs_documents, mds_abs_summaries, 10, f'{output_dir}/task2.10.jsonl')
    save_mds_abstractive_data(cluster_to_documents, abs_documents, mds_abs_summaries, 50, f'{output_dir}/task2.50.jsonl')
    save_mds_abstractive_data(cluster_to_documents, abs_documents, mds_abs_summaries, 100, f'{output_dir}/task2.100.jsonl')
    save_mds_abstractive_data(cluster_to_documents, abs_documents, mds_abs_summaries, 200, f'{output_dir}/task2.200.jsonl')

    save_mds_extractive_data(cluster_to_documents, ext_documents, mds_ext_summaries, 200, f'{output_dir}/task2.200e.jsonl')
    save_mds_extractive_data(cluster_to_documents, ext_documents, mds_ext_summaries, 400, f'{output_dir}/task2.400e.jsonl')
