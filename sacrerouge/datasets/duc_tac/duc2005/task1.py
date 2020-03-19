import argparse
import lxml.html
import re
import tarfile
from collections import defaultdict
from io import BytesIO
from nltk.tokenize import sent_tokenize
from typing import Any, Dict, List

from sacrerouge.io import JsonlWriter


def load_documents(documents_tar_path: str):
    clusters = defaultdict(list)
    documents = {}
    selectors = {}

    with tarfile.open(documents_tar_path, 'r') as tar:
        inner_tar_bytes = tar.extractfile('DUC2005_Summarization_Documents/duc2005_docs.tar.gz').read()
        with tarfile.open(fileobj=BytesIO(inner_tar_bytes)) as inner_tar:
            for member in inner_tar.getmembers():
                if member.isfile():
                    path = member.name.split('/')
                    cluster_id = path[1][:-1]
                    filename = path[2]
                    selector = path[1][-1].upper()
                    clusters[cluster_id].append(filename)
                    if cluster_id not in selectors:
                        selectors[cluster_id] = selector

                    html = inner_tar.extractfile(member).read().decode()
                    tree = lxml.html.document_fromstring(html)
                    text_nodes = list(tree.xpath('//text'))
                    if len(text_nodes) == 0:
                        text_nodes = list(tree.xpath('//graphic'))
                    assert len(text_nodes) == 1

                    text = text_nodes[0].text_content().strip()
                    text = re.sub('\s+', ' ', text)
                    sentences = sent_tokenize(text)
                    documents[filename] = {
                        'filename': filename,
                        'text': sentences
                    }

    return clusters, documents, selectors


def load_summaries(results_tar: str):
    summaries = defaultdict(list)
    with tarfile.open(results_tar, 'r') as tar:
        for member in tar.getmembers():
            if member.name.startswith('results/ROUGE/models/'):
                path = member.name.split('/')
                cluster = path[-1].split('.')[0].lower()
                annotator = path[-1].split('.')[-1]
                sentences = tar.extractfile(member).read().decode(errors='replace').splitlines()
                summary = {
                    'annotator': annotator,
                    'text': sentences
                }
                if summary not in summaries[cluster]:
                    summaries[cluster].append(summary)
    return summaries


def load_topics(topics_file_path: str):
    tree = lxml.html.parse(topics_file_path)
    nodes = list(tree.xpath('//topic'))

    topics = {}
    for node in nodes:
        cluster = node.xpath('num')[0].text_content().strip()[:-1]
        title = node.xpath('title')[0].text_content().strip()

        narr = node.xpath('narr')[0].text_content().strip()
        narr = re.sub('\s+', ' ', narr)
        narr = sent_tokenize(narr)

        granularity = node.xpath('granularity')[0].text_content().strip()
        topics[cluster] = {
            'title': title,
            'narrative': narr,
            'granularity': granularity
        }

    return topics


def save_data(clusters: Dict[str, List[str]],
              documents: Dict[str, List[str]],
              summaries: Dict[str, List[List[str]]],
              topics: Dict[str, Dict[str, Any]],
              selectors: Dict[str, str],
              file_path: str):
    with JsonlWriter(file_path) as out:
        for cluster, doc_ids in clusters.items():
            cluster_docs = [documents[doc_id] for doc_id in doc_ids]
            cluster_summaries = summaries[cluster]
            cluster_topic = topics[cluster]
            cluster_selector = selectors[cluster]
            data = {
                'id': cluster,
                'selector': cluster_selector,
                'topic': cluster_topic,
                'documents': cluster_docs,
                'summaries': cluster_summaries
            }
            if len(cluster_summaries) != 4:
                print(f'Found {len(cluster_summaries)} summaries for cluster {cluster}. Expected 4')
            out.write(data)


def setup(data_root: str, output_dir: str) -> None:
    documents_tar = f'{data_root}/from-nist/DUC2005_Summarization_Documents.tgz'
    results_tar = f'{data_root}/scrapes/duc.nist.gov/past_duc/duc2005/results/NIST/results.tar'
    topics_file_path = f'{data_root}/scrapes/duc.nist.gov/past_duc/duc2005/testdata/duc2005_topics.sgml'
    main(documents_tar, results_tar, topics_file_path, output_dir)


def main(documents_tar, results_tar, topics_file_path, output_dir):
    clusters, documents, selectors = load_documents(documents_tar)
    summaries = load_summaries(results_tar)
    topics = load_topics(topics_file_path)
    save_data(clusters, documents, summaries, topics, selectors, f'{output_dir}/task1.jsonl')


if __name__ == '__main__':
    argp = argparse.ArgumentParser()
    argp.add_argument('documents_tar')
    argp.add_argument('results_tar')
    argp.add_argument('topics_file_path')
    argp.add_argument('output_dir')
    args = argp.parse_args()

    main(args.documents_tar, args.results_tar, args.topics_file_path, args.output_dir)
