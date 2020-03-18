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
    main_documents_ids = defaultdict(list)
    update_documents_ids = defaultdict(lambda: defaultdict(list))
    documents = {}
    selectors = {}
    with tarfile.open(documents_tar_path, 'r') as tar:
        inner_tar_bytes = tar.extractfile('DUC2007_Summarization_Documents/duc2007_testdocs.tar.gz').read()
        with tarfile.open(fileobj=BytesIO(inner_tar_bytes)) as inner_tar:
            for member in inner_tar.getmembers():
                if member.isfile():
                    path = member.name.split('/')
                    filename = path[-1]
                    instance_id = path[2][:-1].lower()

                    selector = path[2][-1]
                    if instance_id not in selectors:
                        selectors[instance_id] = selector

                    if path[1] == 'main':
                        main_documents_ids[instance_id].append(filename)
                    else:
                        group = path[3][-1]
                        update_documents_ids[instance_id][group].append(filename)

                    date = filename[3:11]
                    year, month, day = date[:4], date[4:6], date[6:]
                    date = f'{year}-{month}-{day}'

                    html = inner_tar.extractfile(member).read().decode()
                    tree = lxml.html.document_fromstring(html)

                    headline_nodes = tree.xpath('//headline')
                    if headline_nodes:
                        headline = headline_nodes[0].text_content().strip()
                    else:
                        headline = None

                    text = tree.xpath('//text')[0].text_content().strip()
                    text = re.sub('\s+', ' ', text)
                    sentences = sent_tokenize(text)
                    document = {
                        'filename': filename,
                        'headline': headline,
                        'date': date,
                        'text': sentences
                    }

                    if filename in documents:
                        assert documents[filename] == document
                    else:
                        documents[filename] = document

    return main_documents_ids, update_documents_ids, documents, selectors


def load_main_summaries(main_eval_tar_path: str):
    summaries = defaultdict(list)
    with tarfile.open(main_eval_tar_path, 'r') as tar:
        for member in tar.getmembers():
            if member.name.startswith('mainEval/ROUGE/models/'):
                path = member.name.split('/')
                instance_id = path[-1].split('.')[0].lower()
                annotator = path[-1].split('.')[-1]
                sentences = tar.extractfile(member).read().decode(errors='replace').splitlines()
                summary = {
                    'annotator': annotator,
                    'text': sentences
                }
                summaries[instance_id].append(summary)
    return summaries


def load_update_summaries(update_eval_tar_path: str):
    summaries = defaultdict(lambda: defaultdict(list))
    with tarfile.open(update_eval_tar_path, 'r') as tar:
        for member in tar.getmembers():
            if member.name.startswith('updateEval/ROUGE/models/'):
                path = member.name.split('/')
                instance_id = path[-1].split('.')[0][:-2].lower()
                group = path[-1].split('.')[0][-1]
                annotator = path[-1].split('.')[-1]
                sentences = tar.extractfile(member).read().decode(errors='replace').splitlines()
                summary = {
                    'annotator': annotator,
                    'text': sentences
                }
                summaries[instance_id][group].append(summary)
    return summaries


def load_topics(topics_file_path: str):
    tree = lxml.html.parse(topics_file_path)
    topics = {}
    for node in tree.xpath('//topic'):
        instance_id = node.xpath('num')[0].text_content().strip()[:-1].lower()
        title = node.xpath('title')[0].text_content().strip()
        narr = sent_tokenize(node.xpath('narr')[0].text_content().strip())
        topics[instance_id] = {
            'title': title,
            'narrative': narr
        }
    return topics


def save_main_data(document_ids: Dict[str, List[str]],
                   documents: Dict[str, List[str]],
                   summaries: Dict[str, List[List[str]]],
                   topics: Dict[str, Dict[str, Any]],
                   selectors: Dict[str, str],
                   file_path: str):
    with JsonlWriter(file_path) as out:
        for instance_id in sorted(document_ids.keys()):
            cluster_docs = [documents[doc_id] for doc_id in document_ids[instance_id]]
            cluster_summaries = summaries[instance_id]
            cluster_topic = topics[instance_id]
            selector = selectors[instance_id]
            assert len(cluster_summaries) == 4
            data = {
                'instance_id': instance_id,
                'selector': selector,
                'topic': cluster_topic,
                'documents': cluster_docs,
                'summaries': cluster_summaries
            }
            out.write(data)


def save_update_data(clusters: Dict[str, Dict[str, List[str]]],
                     documents: Dict[str, List[str]],
                     summaries: Dict[str, Dict[str, List[List[str]]]],
                     topics: Dict[str, Dict[str, Any]],
                     selectors: Dict[str, str],
                     file_path_A: str,
                     file_path_B: str,
                     file_path_C: str,
                     file_path_A_B_C: str):
    with JsonlWriter(file_path_A) as out_A:
        with JsonlWriter(file_path_B) as out_B:
            with JsonlWriter(file_path_C) as out_C:
                with JsonlWriter(file_path_A_B_C) as out_A_B_C:
                    for cluster in sorted(clusters.keys()):
                        selector = selectors[cluster]

                        docs1 = [documents[doc_id] for doc_id in clusters[cluster]['A']]
                        docs2 = [documents[doc_id] for doc_id in clusters[cluster]['B']]
                        docs3 = [documents[doc_id] for doc_id in clusters[cluster]['C']]

                        summaries1 = summaries[cluster]['A']
                        summaries2 = summaries[cluster]['B']
                        summaries3 = summaries[cluster]['C']
                        assert len(summaries1) == 4
                        assert len(summaries2) == 4
                        assert len(summaries3) == 4

                        topic = topics[cluster]
                        data_A = {
                            'instance_id': cluster + '-A',
                            'selector': selector,
                            'topic': topic,
                            'documents': docs1,
                            'summaries': summaries1,
                        }
                        data_B = {
                            'instance_id': cluster + '-B',
                            'selector': selector,
                            'topic': topic,
                            'documents': docs2,
                            'summaries': summaries2,
                        }
                        data_C = {
                            'instance_id': cluster + '-C',
                            'selector': selector,
                            'topic': topic,
                            'documents': docs3,
                            'summaries': summaries3,
                        }
                        data_A_B_C = {
                            'instance_id': cluster,
                            'selector': selector,
                            'topic': topic,
                            'documents_A': docs1,
                            'documents_B': docs2,
                            'documents_C': docs3,
                            'summaries_A': summaries1,
                            'summaries_B': summaries2,
                            'summaries_C': summaries3
                        }
                        out_A.write(data_A)
                        out_B.write(data_B)
                        out_C.write(data_C)
                        out_A_B_C.write(data_A_B_C)


def main(args):
    main_documents_ids, update_documents_ids, documents, selectors \
        = load_documents(args.documents_tar)
    main_summaries = load_main_summaries(args.main_eval_tar)
    update_summaries = load_update_summaries(args.update_eval_tar)
    main_topics = load_topics(args.main_topics)
    update_topics = load_topics(args.update_topics)

    save_main_data(main_documents_ids, documents, main_summaries, main_topics, selectors, f'{args.output_dir}/task1.jsonl')
    save_update_data(update_documents_ids, documents, update_summaries, update_topics, selectors,
                     f'{args.output_dir}/task2.A.jsonl',
                     f'{args.output_dir}/task2.B.jsonl',
                     f'{args.output_dir}/task2.C.jsonl',
                     f'{args.output_dir}/task2.A-B-C.jsonl')


if __name__ == '__main__':
    argp = argparse.ArgumentParser()
    argp.add_argument('documents_tar')
    argp.add_argument('main_eval_tar')
    argp.add_argument('update_eval_tar')
    argp.add_argument('main_topics')
    argp.add_argument('update_topics')
    argp.add_argument('output_dir')
    args = argp.parse_args()
    main(args)
