import argparse
import lxml.html
import os
import re
import tarfile
from collections import defaultdict
from io import BytesIO
from nltk.tokenize import sent_tokenize
from typing import Any, Dict, List

from sacrerouge.io import JsonlWriter


def load_task1_and_task2_documents(documents_tar_path: str):
    cluster_to_doc_ids = defaultdict(list)
    documents = {}

    with tarfile.open(documents_tar_path, 'r') as tar:
        for member in tar.getmembers():
            if member.name.startswith('DUC2004_Summarization_Documents/duc2004_testdata/tasks1and2/duc2004_tasks1and2_docs/docs'):
                if member.isfile():
                    path = member.name.split('/')
                    cluster = path[-2][:-1]
                    filename = path[-1]
                    cluster_to_doc_ids[cluster].append(filename)

                    date = filename[3:11]
                    year, month, day = date[:4], date[4:6], date[6:]
                    date = f'{year}-{month}-{day}'

                    html = tar.extractfile(member).read().decode()
                    tree = lxml.html.document_fromstring(html)
                    text_nodes = list(tree.xpath('//text'))
                    assert len(text_nodes) == 1

                    text = text_nodes[0].text_content().strip()
                    text = re.sub('\s+', ' ', text)
                    sentences = sent_tokenize(text)

                    document = {
                        'filename': filename,
                        'date': date,
                        'text': sentences
                    }
                    documents[filename] = document

    print(f'Loaded {len(cluster_to_doc_ids)} clusters and {len(documents)} documents for tasks 1 and 2')
    return cluster_to_doc_ids, documents


def load_task5_documents(documents_tar_path: str):
    cluster_to_doc_ids = defaultdict(list)
    documents = {}

    with tarfile.open(documents_tar_path, 'r') as tar:
        for member in tar.getmembers():
            if member.name.startswith('DUC2004_Summarization_Documents/duc2004_testdata/task5/duc2004_task5_docs/docs'):
                if member.isfile():
                    path = member.name.split('/')
                    cluster = path[-2][:-1]
                    filename = path[-1]
                    cluster_to_doc_ids[cluster].append(filename)

                    date = filename[3:11]
                    year, month, day = date[:4], date[4:6], date[6:]
                    date = f'{year}-{month}-{day}'

                    html = tar.extractfile(member).read().decode()
                    tree = lxml.html.document_fromstring(html)
                    text_nodes = list(tree.xpath('//text'))
                    assert len(text_nodes) == 1

                    text = text_nodes[0].text_content().strip()
                    text = re.sub('\s+', ' ', text)
                    sentences = sent_tokenize(text)

                    document = {
                        'filename': filename,
                        'date': date,
                        'text': sentences
                    }
                    documents[filename] = document

    print(f'Loaded {len(cluster_to_doc_ids)} clusters and {len(documents)} documents for task 5')
    return cluster_to_doc_ids, documents


def load_task5_topics(documents_tar_path: str):
    topics = {}
    with tarfile.open(documents_tar_path, 'r') as tar:
        member = tar.extractfile('DUC2004_Summarization_Documents/duc2004_testdata/task5/duc2004.task5.topicsets')
        lines = member.read().decode().splitlines()
        for line in lines[7:]:
            cluster, topic = line.strip().split('\t')
            cluster = cluster[:-1]
            topics[cluster] = topic

    print(f'Loaded {len(topics)} topics')
    return topics


def load_task1_summaries(results_tar: str):
    summaries = defaultdict(list)
    with tarfile.open(results_tar, 'r') as tar:
        inner_tar_bytes = tar.extractfile('duc2004_results/ROUGE/duc2004.task1.ROUGE.models.tar.gz').read()
        with tarfile.open(fileobj=BytesIO(inner_tar_bytes)) as inner_tar:
            for member in inner_tar.getmembers():
                filename = os.path.basename(member.name)
                parts = filename.split('.')
                filename = parts[-2] + '.' + parts[-1]

                text = [inner_tar.extractfile(member).read().decode().strip()]
                summary = {
                    'text': text
                }

                if summary not in summaries[filename]:
                    summaries[filename].append(summary)
                else:
                    print(f'Skipping duplicate summary for document {filename}')

    num_summaries = sum(len(s) for s in summaries.values())
    print(f'Loaded {num_summaries} summaries for task 1')
    return summaries


def load_task2_summaries(results_tar: str):
    summaries = defaultdict(list)
    with tarfile.open(results_tar, 'r') as tar:
        inner_tar_bytes = tar.extractfile('duc2004_results/ROUGE/duc2004.task2.ROUGE.models.tar.gz').read()
        with tarfile.open(fileobj=BytesIO(inner_tar_bytes)) as inner_tar:
            for member in inner_tar.getmembers():
                filename = os.path.basename(member.name)
                parts = filename.split('.')
                cluster = parts[0].lower()

                sentences = inner_tar.extractfile(member).read().decode().splitlines()
                summary = {
                    'text': sentences
                }
                if summary not in summaries[cluster]:
                    summaries[cluster].append(summary)
                else:
                    print(f'Skipping duplicate summary for cluster {cluster}')

    num_summaries = sum(len(s) for s in summaries.values())
    print(f'Loaded {num_summaries} summaries for task 2')
    return summaries


def load_task5_summaries(results_tar: str):
    summaries = defaultdict(list)
    with tarfile.open(results_tar, 'r') as tar:
        inner_tar_bytes = tar.extractfile('duc2004_results/ROUGE/duc2004.task5.ROUGE.models.tar.gz').read()
        with tarfile.open(fileobj=BytesIO(inner_tar_bytes)) as inner_tar:
            for member in inner_tar.getmembers():
                filename = os.path.basename(member.name)
                parts = filename.split('.')
                cluster = parts[0].lower()

                sentences = inner_tar.extractfile(member).read().decode().splitlines()
                summary = {
                    'text': sentences
                }
                if summary not in summaries[cluster]:
                    summaries[cluster].append(summary)
                else:
                    print(f'Skipping duplicate summary for cluster {cluster}')

    num_summaries = sum(len(s) for s in summaries.values())
    print(f'Loaded {num_summaries} summaries for task 5')
    return summaries


def save_task1_data(documents: Dict[str, List[str]],
                    summaries: Dict[str, List[List[str]]],
                    file_path: str):
    with JsonlWriter(file_path) as out:
        for doc_id, document in documents.items():
            doc_summaries = summaries[doc_id]
            data = {
                'instance_id': doc_id,
                'document': document,
                'summaries': doc_summaries
            }
            if len(doc_summaries) != 4:
                print(f'Task 1 document {doc_id} has {len(doc_summaries)} summaries. Expected 4')
            out.write(data)


def save_task2_data(cluster_to_doc_ids: Dict[str, List[str]],
                    documents: Dict[str, List[str]],
                    summaries: Dict[str, List[List[str]]],
                    file_path: str):
    with JsonlWriter(file_path) as out:
        for cluster, doc_ids in cluster_to_doc_ids.items():
            cluster_docs = [documents[doc_id] for doc_id in doc_ids]
            cluster_summaries = summaries[cluster]
            data = {
                'instance_id': cluster,
                'documents': cluster_docs,
                'summaries': cluster_summaries
            }
            if len(cluster_summaries) != 4:
                print(f'Task 2 cluster {cluster} has {len(cluster_summaries)} summaries. Expected 4')
            out.write(data)


def save_task5_data(cluster_to_doc_ids: Dict[str, List[str]],
                    documents: Dict[str, List[str]],
                    summaries: Dict[str, List[List[str]]],
                    topics: Dict[str, str],
                    file_path: str):
    with JsonlWriter(file_path) as out:
        for cluster, doc_ids in cluster_to_doc_ids.items():
            cluster_docs = [documents[doc_id] for doc_id in doc_ids]
            cluster_summaries = summaries[cluster]
            cluster_topic = topics[cluster]
            data = {
                'instance_id': cluster,
                'topic': cluster_topic,
                'documents': cluster_docs,
                'summaries': cluster_summaries
            }
            if len(cluster_summaries) != 4:
                print(f'Task 5 cluster {cluster} has {len(cluster_summaries)} summaries. Expected 4')
            out.write(data)


def setup(data_root: str, output_dir: str) -> None:
    documents_tar = f'{data_root}/from-nist/DUC2004_Summarization_Documents.tgz'
    results_tar = f'{data_root}/scrapes/duc.nist.gov/past_duc/duc2004/duc2004_results.tgz'
    main(documents_tar, results_tar, output_dir)


def main(documents_tar, results_tar, output_dir):
    cluster_to_doc_ids, documents = load_task1_and_task2_documents(documents_tar)
    task_1_summaries = load_task1_summaries(results_tar)
    save_task1_data(documents, task_1_summaries, f'{output_dir}/task1.jsonl')

    task_2_summaries = load_task2_summaries(results_tar)
    save_task2_data(cluster_to_doc_ids, documents, task_2_summaries, f'{output_dir}/task2.jsonl')

    cluster_to_doc_ids, documents = load_task5_documents(documents_tar)
    topics = load_task5_topics(documents_tar)
    task_5_summaries = load_task5_summaries(results_tar)
    save_task5_data(cluster_to_doc_ids, documents, task_5_summaries, topics, f'{output_dir}/task5.jsonl')


if __name__ == '__main__':
    argp = argparse.ArgumentParser()
    argp.add_argument('documents_tar')
    argp.add_argument('results_tar')
    argp.add_argument('topics_file_path')
    argp.add_argument('output_dir')
    args = argp.parse_args()

    main(args.documents_tar, args.results_tar, args.topics_file_path, args.output_dir)
