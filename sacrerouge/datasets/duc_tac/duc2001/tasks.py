"""
Parses the DUC 2001 single- and multi-document summarization datasets. These
correspond to task 1 and task 2 from the competition. There are several peculiarities
about the dataset which we have tried to address, but it's possible we did not
get everything.
"""
import argparse
import lxml.html
import os
import re
import tarfile
from collections import defaultdict
from nltk.tokenize import sent_tokenize
from typing import Dict, List

from sacrerouge.io import JsonlWriter

# There are several typos in the 'perdocs' files in which the document
# id is incorrect. This provides a mapping from the incorrect id to the
# correct one
per_doc_summary_doc_id_fix = {
    'SMN91-06154062': 'SJMN91-06154062',
    'AP870611-0085': 'WSJ870611-0085',
    'SJMN91-0605144': 'SJMN91-06015144',
    'APP890515-0232': 'AP890515-0232',
    'WSJ891125-0090': 'AP891125-0090',
    'FT931-100514': 'FT931-10514',
    'FB153-57782': 'FBIS3-57782',
    'FBIS4-45908': 'FBIS-45908',
    'FBIS3-41815': 'FBIS-41815',
    'FBIS4-45908': 'FBIS-45908',
    'FBIS4-35908': 'FBIS-45908',
    'AP890325-0143': 'AP830325-0143',
    'LA081489-0225': 'LA081489-0025'
}

document_blacklist = [
    'FBIS-41815~'
]


def load_sjmn_document(tar, member) -> str:
    html = tar.extractfile(member).read().decode()
    tree = lxml.html.document_fromstring(html)
    text = []
    for node in tree.xpath('body/doc/leadpara | body/doc/text'):
        content = node.text_content().strip()

        # The SJMN files have sentences which end in '.;'. My guess is that
        # these mark paragraphs, but I don't know how to confirm that
        content = re.sub('\.;\s+', '. ', content)

        # There are a lot of quotes that end with semicolons that messes
        # up the sentence splitting logic
        content = re.sub('";', '"', content)

        # The newlines are meaningless since they often appear in the middle
        # of a sentence
        content = re.sub('\s+', ' ', content)
        text.append(content)

    text = ' '.join(text)
    return text


def load_wsj_document(tar, member) -> str:
    html = tar.extractfile(member).read().decode()
    tree = lxml.html.document_fromstring(html)
    text = []
    for node in tree.xpath('body/doc/lp | body/doc/text'):
        # The paragraphs seem to be indented with extra whitespace
        content = node.text_content().strip()
        content = re.sub('\s+', ' ', content)
        text.append(content)
    text = ' '.join(text)
    return text


def load_ap_document(tar, member) -> str:
    html = tar.extractfile(member).read().decode()
    tree = lxml.html.document_fromstring(html)
    # There is no lead paragraph for the AP documents.
    body = tree.xpath('body/doc/text')[0].text_content().strip()

    # The paragraphs seem to be indented with extra whitespace
    body = re.sub('\s+', ' ', body)
    return body


def load_la_document(tar, member) -> str:
    html = tar.extractfile(member).read().decode()
    tree = lxml.html.document_fromstring(html)
    body = tree.xpath('body/doc/text')[0].text_content().strip()

    # The paragraphs are separated by <P> tags, but the `text_content` function
    # retrieves all of the text from the descendants, so those are removed
    body = re.sub('\s+', ' ', body)
    return body


def load_fbis_document(tar, member) -> str:
    # The FBIS documents often have some metadata at the beginning of the
    # <text> tag which isn't removed here
    html = tar.extractfile(member).read().decode()
    tree = lxml.html.document_fromstring(html)
    body = tree.xpath('body/doc/text')[0].text_content().strip()

    # The paragraphs seem to be indented with extra whitespace
    body = re.sub('\s+', ' ', body)
    return body


def load_ft_document(tar, member) -> str:
    html = tar.extractfile(member).read().decode()
    tree = lxml.html.document_fromstring(html)
    body = tree.xpath('body/doc/text')[0].text_content().strip()

    # The paragraphs seem to be indented with extra whitespace
    body = re.sub('\s+', ' ', body)
    return body


def load_document(tar, member) -> List[str]:
    filename = os.path.basename(member.name)
    if filename.startswith('SJMN'):
        text = load_sjmn_document(tar, member)
    elif filename.startswith('WSJ'):
        text = load_wsj_document(tar, member)
    elif filename.startswith('AP'):
        text = load_ap_document(tar, member)
    elif filename.startswith('LA'):
        text = load_la_document(tar, member)
    elif filename.startswith('FBIS'):
        text = load_fbis_document(tar, member)
    elif filename.startswith('FT'):
        text = load_ft_document(tar, member)
    else:
        raise Exception(member.name)

    # Many quotes have '. . .' which mess up the sentence splitting
    text = re.sub(r'\. \. \.', '...', text)

    sentences = sent_tokenize(text)
    return {
        'filename': filename,
        'text': sentences
    }


def load_mds_summary(tar, member) -> List[str]:
    """
    Loads a multi-document summary from the file path and returns the
    sentence-tokenized summary.
    """
    html = tar.extractfile(member).read().decode()
    tree = lxml.html.document_fromstring(html)
    text = tree.xpath('body/sum')[0].text_content().strip()
    text = re.sub('\s+', ' ', text)
    sentences = sent_tokenize(text)

    dirname = os.path.basename(os.path.dirname(member.name))
    annotator = dirname[-1].upper()
    return {
        'annotator': annotator,
        'text': sentences
    }


def load_sds_summaries(tar, member) -> Dict[str, List[str]]:
    """
    Loads all of the individual single-document summaries and returns them as
    a dictionary mapping from the document ID to the sentence-tokenized summary.
    """
    html = tar.extractfile(member).read().decode()

    # The perdocs file for d35ff is missing a closing angle bracket
    # on one of the tags, which messes up the parser
    if os.path.basename(os.path.dirname(member.name)) == 'd35ff':
        html = html[:768] + '>' + html[768:]
    tree = lxml.html.document_fromstring(html)

    dirname = os.path.basename(os.path.dirname(member.name))
    annotator = dirname[-1].upper()

    summaries = {}
    for node in tree.xpath('body/sum'):
        doc = node.attrib['docref']
        if doc in per_doc_summary_doc_id_fix:
            doc = per_doc_summary_doc_id_fix[doc]

        text = node.text_content().strip()
        text = re.sub('\s+', ' ', text)
        sentences = sent_tokenize(text)
        summaries[doc] = {
            'annotator': annotator,
            'text': sentences
        }
    return summaries


def load_training_data(documents_tar: str):
    # ``cluster_to_doc_ids`` maps from the cluster name to the list of
    # document IDs that belong to the cluster
    cluster_to_doc_ids = defaultdict(list)
    # ``documents`` maps from the document ID to the ``List[str]`` document
    documents = {}
    # ``mds_summaries`` maps from the cluster name then summary length to the summary
    mds_summaries = defaultdict(lambda: defaultdict(list))
    # ``sds_summaries`` maps from the file name to the summary
    sds_summaries = defaultdict(list)

    with tarfile.open(documents_tar, 'r') as tar:
        for member in tar.getmembers():
            if member.isfile():
                if member.name.startswith('DUC2001_Summarization_Documents/data/training'):
                    path = member.name.split('/')
                    cluster = path[3][:-1]
                    filename = path[-1]

                    if filename == 'perdocs':
                        summaries = load_sds_summaries(tar, member)
                        for doc_id in sorted(summaries.keys()):
                            sds_summaries[doc_id].append(summaries[doc_id])
                    elif filename in ['50', '100', '200', '400']:
                        summary = load_mds_summary(tar, member)
                        mds_summaries[cluster][filename].append(summary)
                    elif len(path) >= 5 and path[4] == 'docs':
                        document = load_document(tar, member)
                        cluster_to_doc_ids[cluster].append(filename)
                        documents[filename] = document

    return cluster_to_doc_ids, documents, mds_summaries, sds_summaries


def load_test_data(documents_tar: str):
    # ``cluster_to_doc_ids`` maps from the cluster name to the list of
    # document IDs that belong to the cluster
    cluster_to_doc_ids = defaultdict(list)
    # ``documents`` maps from the document ID to the ``List[str]`` document
    documents = {}
    # ``mds_summaries`` maps from the cluster name then summary length to the summaries
    mds_summaries = defaultdict(lambda: defaultdict(list))
    # ``sds_summaries`` maps from the file name to the summary
    sds_summaries = defaultdict(list)

    with tarfile.open(documents_tar, 'r') as tar:
        for member in tar.getmembers():
            if member.isfile():
                if member.name.startswith('DUC2001_Summarization_Documents/data/test/docs'):
                    path = member.name.split('/')
                    if len(path) != 6:
                        continue
                    cluster = path[-2][:-1]
                    doc_id = path[-1]
                    if doc_id in document_blacklist:
                        continue
                    cluster_to_doc_ids[cluster].append(doc_id)

                    document = load_document(tar, member)
                    documents[doc_id] = document
                elif member.name.startswith('DUC2001_Summarization_Documents/data/test/original.summaries') or member.name.startswith('DUC2001_Summarization_Documents/data/test/duplicate.summaries'):
                    path = member.name.split('/')
                    if len(path) != 6:
                        continue
                    cluster = path[-2][:-2]
                    filename = path[-1]
                    if filename == 'perdocs':
                        summaries = load_sds_summaries(tar, member)
                        for doc_id in sorted(summaries.keys()):
                            sds_summaries[doc_id].append(summaries[doc_id])
                    elif filename in ['50', '100', '200', '400']:
                        summary = load_mds_summary(tar, member)
                        mds_summaries[cluster][filename].append(summary)

    return cluster_to_doc_ids, documents, mds_summaries, sds_summaries


def save_sds_training_data(documents: Dict[str, List[str]],
                           summaries: Dict[str, List[List[str]]],
                           file_path: str) -> None:
    with JsonlWriter(file_path) as out:
        assert set(documents.keys()) == set(summaries.keys())
        for doc_id in sorted(documents.keys()):
            document = documents[doc_id]
            doc_summaries = summaries[doc_id]
            # This document appears in two clusters and so it has two
            # single document summaries
            if doc_id == 'SJMN91-06170171':
                assert len(doc_summaries) == 2
            else:
                assert len(doc_summaries) == 1
            data = {
                'instance_id': doc_id,
                'document': document,
                'summaries': doc_summaries
            }
            out.write(data)


def save_sds_test_data(documents: Dict[str, List[str]],
                       summaries: Dict[str, List[List[str]]],
                       file_path: str) -> None:
    with JsonlWriter(file_path) as out:
        for doc_id in sorted(documents.keys()):
            document = documents[doc_id]
            doc_summaries = summaries[doc_id]
            # The original summaries for cluster d14 is missing a summary
            # for document FBIS4-4674 and likewise for dd44 and FT934-10911
            if doc_id in ['FBIS4-4674', 'FT934-10911']:
                assert len(doc_summaries) == 2
            else:
                assert len(doc_summaries) == 3, doc_id
            data = {
                'instance_id': doc_id,
                'document': document,
                'summaries': doc_summaries
            }
            out.write(data)


def save_mds_training_data(cluster_to_doc_ids: Dict[str, List[str]],
                           documents: Dict[str, List[str]],
                           summaries: Dict[str, Dict[str, List[str]]],
                           length: str,
                           file_path: str) -> None:
    with JsonlWriter(file_path) as out:
        assert set(cluster_to_doc_ids.keys()) == set(summaries.keys())
        for cluster in sorted(cluster_to_doc_ids.keys()):
            doc_ids = cluster_to_doc_ids[cluster]
            cluster_documents = [documents[doc_id] for doc_id in sorted(doc_ids)]
            summary = summaries[cluster][length]
            data = {
                'instance_id': cluster,
                'documents': cluster_documents,
                'summaries': [summary]
            }
            out.write(data)


def save_mds_test_data(cluster_to_doc_ids: Dict[str, List[str]],
                       documents: Dict[str, List[str]],
                       summaries: Dict[str, Dict[str, List[str]]],
                       length: str,
                       file_path: str) -> None:
    with JsonlWriter(file_path) as out:
        for cluster in sorted(cluster_to_doc_ids.keys()):
            doc_ids = cluster_to_doc_ids[cluster]
            cluster_documents = [documents[doc_id] for doc_id in sorted(doc_ids)]
            cluster_summaries = summaries[cluster][length]
            if cluster == 'd31':
                assert len(cluster_summaries) == 2
            else:
                assert len(cluster_summaries) == 3
            data = {
                'instance_id': cluster,
                'documents': cluster_documents,
                'summaries': cluster_summaries
            }
            out.write(data)


def setup(data_root: str, output_dir: str) -> None:
    documents_tar = f'{data_root}/from-nist/DUC2001_Summarization_Documents.tgz'
    main(documents_tar, output_dir)


def main(documents_tar, output_dir):
    cluster_to_doc_ids, documents, mds_summaries, sds_summaries \
        = load_training_data(documents_tar)

    train_sds_path = f'{output_dir}/task1.train.jsonl'
    save_sds_training_data(documents, sds_summaries, train_sds_path)

    train_mds_50_path = f'{output_dir}/task2.train.50.jsonl'
    train_mds_100_path = f'{output_dir}/task2.train.100.jsonl'
    train_mds_200_path = f'{output_dir}/task2.train.200.jsonl'
    train_mds_400_path = f'{output_dir}/task2.train.400.jsonl'
    save_mds_training_data(cluster_to_doc_ids, documents, mds_summaries, "50", train_mds_50_path)
    save_mds_training_data(cluster_to_doc_ids, documents, mds_summaries, "100", train_mds_100_path)
    save_mds_training_data(cluster_to_doc_ids, documents, mds_summaries, "200", train_mds_200_path)
    save_mds_training_data(cluster_to_doc_ids, documents, mds_summaries, "400", train_mds_400_path)

    cluster_to_doc_ids, documents, mds_summaries, sds_summaries = \
        load_test_data(documents_tar)

    test_sds_path = f'{output_dir}/task1.test.jsonl'
    save_sds_test_data(documents, sds_summaries, test_sds_path)

    test_mds_50_path = f'{output_dir}/task2.test.50.jsonl'
    test_mds_100_path = f'{output_dir}/task2.test.100.jsonl'
    test_mds_200_path = f'{output_dir}/task2.test.200.jsonl'
    test_mds_400_path = f'{output_dir}/task2.test.400.jsonl'
    save_mds_test_data(cluster_to_doc_ids, documents, mds_summaries, "50", test_mds_50_path)
    save_mds_test_data(cluster_to_doc_ids, documents, mds_summaries, "100", test_mds_100_path)
    save_mds_test_data(cluster_to_doc_ids, documents, mds_summaries, "200", test_mds_200_path)
    save_mds_test_data(cluster_to_doc_ids, documents, mds_summaries, "400", test_mds_400_path)