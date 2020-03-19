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
        inner_tar_bytes = tar.extractfile('DUC2006_Summarization_Documents/duc2006_docs.tar.gz').read()
        with tarfile.open(fileobj=BytesIO(inner_tar_bytes)) as inner_tar:
            for member in inner_tar.getmembers():
                if member.isfile():
                    path = member.name.split('/')
                    filename = path[2]
                    instance_id = path[1][:-1].lower()
                    selector = path[1][-1]

                    clusters[instance_id].append(filename)

                    if instance_id not in selectors:
                        selectors[instance_id] = selector

                    date = filename[3:11]
                    year, month, day = date[:4], date[4:6], date[6:]
                    date = f'{year}-{month}-{day}'

                    html = inner_tar.extractfile(member).read().decode()
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

    return clusters, documents, selectors


def load_summaries(eval_tar_path: str):
    summaries = defaultdict(list)
    with tarfile.open(eval_tar_path, 'r') as tar:
        for member in tar.getmembers():
            if member.name.startswith('NISTeval/ROUGE/models/'):
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
        cluster = node.xpath('num')[0].text_content().strip()[:-1].lower()
        title = node.xpath('title')[0].text_content().strip()

        narr = node.xpath('narr')[0].text_content().strip()
        narr = re.sub('\s+', ' ', narr)
        narr = sent_tokenize(narr)

        topics[cluster] = {
            'title': title,
            'narrative': narr
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
                'instance_id': cluster,
                'selector': cluster_selector,
                'topic': cluster_topic,
                'documents': cluster_docs,
                'summaries': cluster_summaries
            }
            if len(cluster_summaries) != 4:
                print(f'Found {len(cluster_summaries)} summaries for cluster {cluster}. Expected 4')
            out.write(data)


def setup(data_root: str, output_dir: str):
    documents_tar = f'{data_root}/from-nist/DUC2006_Summarization_Documents.tgz'
    eval_tar = f'{data_root}/scrapes/duc.nist.gov/past_duc_aquaint/duc2006/results/NIST/NISTeval.tar.gz'
    topics_file_path = f'{data_root}/scrapes/duc.nist.gov/past_duc_aquaint/duc2006/testdata/duc2006_topics.sgml'
    main(documents_tar, eval_tar, topics_file_path, output_dir)


def main(documents_tar, eval_tar, topics_file_path, output_dir):
    clusters, documents, selectors = load_documents(documents_tar)
    summaries = load_summaries(eval_tar)
    topics = load_topics(topics_file_path)
    save_data(clusters, documents, summaries, topics, selectors, f'{output_dir}/task1.jsonl')


if __name__ == '__main__':
    argp = argparse.ArgumentParser()
    argp.add_argument('documents_tar')
    argp.add_argument('eval_tar')
    argp.add_argument('topics_file_path')
    argp.add_argument('output_dir')
    args = argp.parse_args()
    main(args)
