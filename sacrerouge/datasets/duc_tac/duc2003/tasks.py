import argparse
import json
import lxml.html
import re
import tarfile
from collections import defaultdict
from io import BytesIO
from nltk.tokenize import sent_tokenize
from typing import Any, Dict, List

from sacrerouge.io import JsonlWriter


def parse_document(html: str) -> List[str]:
    tree = lxml.html.document_fromstring(html)
    nodes = list(tree.xpath('//text'))
    if not nodes:
        nodes = list(tree.xpath('//graphic'))
    root = nodes[0]
    text = root.text_content().strip()
    text = re.sub(r'\s+', ' ', text)
    sentences = sent_tokenize(text)
    return sentences


def load_task1_documents(documents_tar: str):
    print('Loading Task 1 Documents')
    cluster_to_doc_ids, documents = defaultdict(list), {}
    with tarfile.open(documents_tar, 'r') as tar:
        inner_tar_bytes = tar.extractfile('DUC2003_Summarization_Documents/duc2003_testdata/task1/task1.docs.tar.gz').read()
        with tarfile.open(fileobj=BytesIO(inner_tar_bytes)) as inner_tar:
            for member in inner_tar.getmembers():
                if member.isfile():
                    _, _, cluster, doc_id = member.name.split('/')
                    cluster_to_doc_ids[cluster].append(doc_id)

                    text = inner_tar.extractfile(member).read().decode()
                    sentences = parse_document(text)
                    document = {
                        'filename': doc_id,
                        'text': sentences
                    }
                    if doc_id in documents:
                        assert documents[doc_id] == document
                    documents[doc_id] = document
                    print(f'Loaded document {doc_id} in cluster {cluster}')
    return cluster_to_doc_ids, documents


def load_task2_documents(documents_tar: str):
    cluster_to_doc_ids, documents = defaultdict(list), {}
    with tarfile.open(documents_tar, 'r') as tar:
        inner_tar_bytes = tar.extractfile('DUC2003_Summarization_Documents/duc2003_testdata/task2/task2.docs.tar.gz').read()
        with tarfile.open(fileobj=BytesIO(inner_tar_bytes)) as inner_tar:
            for member in inner_tar.getmembers():
                if member.isfile():
                    _, _, cluster, doc_id = member.name.split('/')
                    cluster = cluster[:-1]
                    cluster_to_doc_ids[cluster].append(doc_id)

                    text = inner_tar.extractfile(member).read().decode()
                    sentences = parse_document(text)
                    document = {
                        'filename': doc_id,
                        'text': sentences
                    }
                    if doc_id in documents:
                        assert documents[doc_id] == document
                    documents[doc_id] = document
    return cluster_to_doc_ids, documents


def load_task2_topics(documents_tar: str):
    metadata = json.loads(open('datasets/duc-tac/duc2003/topics-metadata.json', 'r').read())
    with tarfile.open(documents_tar, 'r') as tar:
        text = tar.extractfile('DUC2003_Summarization_Documents/duc2003_testdata/task2/topics').read().decode()

    topics = {}
    for info in metadata:
        cluster = 'd' + info['cluster']

        start, end = info['title']
        title = text[start:end]

        event = {}
        for wh, (start, end) in info['event'].items():
            event[wh] = re.sub(f'\s+', ' ', text[start:end])

        start, end = info['explication']
        explication = sent_tokenize(re.sub(f'\s+', ' ', text[start:end]))

        topics[cluster] = {
            'title': title,
            'event': event,
            'explication': explication
        }
    return topics


def load_task3_documents(documents_tar: str):
    cluster_to_doc_ids, documents = defaultdict(list), {}
    with tarfile.open(documents_tar, 'r') as tar:
        inner_tar_bytes = tar.extractfile('DUC2003_Summarization_Documents/duc2003_testdata/task3/task3.docs.tar.gz').read()
        with tarfile.open(fileobj=BytesIO(inner_tar_bytes)) as inner_tar:
            for member in inner_tar.getmembers():
                if member.isfile():
                    _, _, cluster, doc_id = member.name.split('/')
                    cluster = cluster[:-1]
                    cluster_to_doc_ids[cluster].append(doc_id)

                    text = inner_tar.extractfile(member).read().decode()
                    sentences = parse_document(text)
                    document = {
                        'filename': doc_id,
                        'text': sentences
                    }
                    if doc_id in documents:
                        assert documents[doc_id] == document
                    documents[doc_id] = document
    return cluster_to_doc_ids, documents


def load_task3_viewpoints(documents_tar: str) -> Dict[str, str]:
    viewpoints = {}
    with tarfile.open(documents_tar, 'r') as tar:
        inner_tar_bytes = tar.extractfile('DUC2003_Summarization_Documents/duc2003_testdata/task3/viewpoints.given.to.systems.tar.gz').read()
        with tarfile.open(fileobj=BytesIO(inner_tar_bytes)) as inner_tar:
            for member in inner_tar.getmembers():
                _, _, cluster, _ = member.name.split('/')
                cluster = cluster[:-2]

                lines = inner_tar.extractfile(member).read().decode().splitlines()
                lines = list(filter(None, lines))
                viewpoint = []
                for line in lines:
                    if (line.startswith('<VIEWPOINT') or line.startswith('DOCSET=') or
                       line.startswith('CREATOR=') or line.startswith('</VIEWPOINT>')):
                        continue
                    viewpoint.append(line.strip())
                viewpoint = ' '.join(viewpoint)
                viewpoints[cluster] = viewpoint
    return viewpoints


def load_task4_abstractive_documents(documents_tar: str):
    cluster_to_doc_ids, documents = defaultdict(list), {}
    with tarfile.open(documents_tar, 'r') as tar:
        inner_tar_bytes = tar.extractfile('DUC2003_Summarization_Documents/duc2003_testdata/task4/task4.docs.tar.gz').read()
        with tarfile.open(fileobj=BytesIO(inner_tar_bytes)) as inner_tar:
            for member in inner_tar.getmembers():
                _, _, cluster, doc_id = member.name.split('/')
                cluster = cluster[:-1]
                cluster_to_doc_ids[cluster].append(doc_id)

                text = inner_tar.extractfile(member).read().decode(errors='ignore')
                sentences = parse_document(text)
                document = {
                    'filename': doc_id,
                    'text': sentences
                }
                if doc_id in documents:
                    assert documents[doc_id] == document
                documents[doc_id] = document
    return cluster_to_doc_ids, documents


def load_task4_extractive_documents(documents_tar: str):
    cluster_to_doc_ids, documents = defaultdict(set), defaultdict(list)
    with tarfile.open(documents_tar, 'r') as tar:
        for member in tar.getmembers():
            if member.isfile() and member.name.startswith('DUC2003_Summarization_Documents/trec2002_novelty_docs'):
                path = member.name.split('/')
                cluster = 'd' + path[-1][:3]

                html = tar.extractfile(member).read().decode(errors='replace')
                tree = lxml.html.document_fromstring(html)
                for doc_node in tree.xpath('//doc'):
                    sentences = []
                    # //s from doc_node retrieves all the sentences across
                    # all of the documents. Not sure why
                    for sent_node in doc_node.iter('s'):
                        doc_id = sent_node.get('docid')
                        sentence = sent_node.text_content().strip()
                        sentences.append(sentence)
                        cluster_to_doc_ids[cluster].add(doc_id)
                    document = {
                        'filename': doc_id,
                        'text': sentences
                    }
                    documents[doc_id] = document
    return cluster_to_doc_ids, documents


def load_task4_sentence_labels(documents_tar: str):
    summaries = {}
    with tarfile.open(documents_tar, 'r') as tar:
        inner_tar_bytes = tar.extractfile('DUC2003_Summarization_Documents/duc2003_testdata/task4/task4.sentences.tar.gz').read()
        with tarfile.open(fileobj=BytesIO(inner_tar_bytes)) as inner_tar:
            for member in inner_tar.getmembers():
                _, _, filename = member.name.split('/')
                cluster = 'd' + filename[:3]
                html = inner_tar.extractfile(member).read().decode(errors='ignore')
                tree = lxml.html.document_fromstring(html)
                labels = []
                for node in tree.xpath('//s'):
                    doc_id = node.get('docid')
                    num = int(node.get('num')) - 1
                    is_novel = 'novel' in node.attrib
                    labels.append({
                        'filename': doc_id,
                        'sent_index': num,
                        'is_novel': is_novel
                    })
                summaries[cluster] = labels
    return summaries


def split_into_tags(lines: List[str]) -> List[List[str]]:
    tags = []
    current = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith('<'):
            # New tag
            if current:
                tags.append(current)
            current = [line]
        else:
            current.append(line)
    if current:
        tags.append(current)
    return tags


def group_by_clusters(tags: List[List[str]]) -> List[List[List[str]]]:
    groups = []
    current = []
    for tag in tags:
        if tag == ['<top>']:
            if current:
                groups.append(current)
            current = []
        else:
            current.append(tag)
    if current:
        groups.append(current)
    return groups


def load_task4_questions(documents_tar: str):
    with tarfile.open(documents_tar, 'r') as tar:
        lines = tar.extractfile('DUC2003_Summarization_Documents/duc2003_testdata/task4/duc.novelty_topics.txt').read().decode().splitlines()

    tags = split_into_tags(lines)
    groups = group_by_clusters(tags)

    questions = {}
    for group in groups:
        assert group[0][0].startswith('<num>')
        assert group[1][0].startswith('<title>')
        assert group[2][0].startswith('<desc>')
        assert group[3][0].startswith('<desc2>')
        assert group[4][0].startswith('<narr>')

        cluster = 'd' + group[0][0][len('<num> Number: '):]
        title = group[1][0][len('<title> '):]
        desc1 = ' '.join(group[2][1:])
        desc2 = ' '.join(group[3][1:])
        narr = sent_tokenize(' '.join(group[4][1:]))
        assert cluster not in questions, cluster
        questions[cluster] = {
            'title': title,
            'description1': desc1,
            'description2': desc2,
            'narrative': narr
        }
    return questions


def load_summaries(summaries_tar: str):
    sds, mds = defaultdict(list), defaultdict(list)

    with tarfile.open(summaries_tar, 'r') as tar:
        for member in tar.getmembers():
            if member.isfile():
                sentences = tar.extractfile(member).read().decode().strip().splitlines()
                sentences = ' '.join(list(map(lambda line: line.strip(), sentences)))
                sentences = sent_tokenize(sentences)

                path = member.name.split('/')
                filename = path[-1]
                sections = filename.split('.')
                annotator = sections[4]
                summary = {
                    'annotator': annotator,
                    'text': sentences
                }

                is_multi = sections[1] == 'M'
                if is_multi:
                    assert len(sections) == 5
                    cluster = sections[0].lower()
                    if summary not in mds[cluster]:
                        mds[cluster].append(summary)
                    else:
                        print(f'Cluster {cluster} has duplicate summaries')
                else:
                    assert len(sections) == 7
                    doc_id = '.'.join(sections[5:7])
                    assert summary not in sds[doc_id]
                    sds[doc_id].append(summary)
    return sds, mds


def save_task1_data(documents: Dict[str, List[str]],
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


def save_task2_data(cluster_to_doc_ids: Dict[str, List[str]],
                    documents: Dict[str, List[str]],
                    summaries: Dict[str, List[List[str]]],
                    topics: Dict[str, Dict[str, Any]],
                    file_path: str) -> None:
    with JsonlWriter(file_path) as out:
        for cluster in sorted(cluster_to_doc_ids.keys()):
            cluster_docs = [documents[doc_id] for doc_id in cluster_to_doc_ids[cluster]]
            cluster_summaries = summaries[cluster]
            cluster_topic = topics[cluster]
            data = {
                'instance_id': cluster,
                'topic': cluster_topic,
                'documents': cluster_docs,
                'summaries': cluster_summaries
            }
            out.write(data)


def save_task3_data(cluster_to_doc_ids: Dict[str, List[str]],
                    documents: Dict[str, List[str]],
                    summaries: Dict[str, List[List[str]]],
                    viewpoints: Dict[str, str],
                    file_path: str) -> None:
    with JsonlWriter(file_path) as out:
        for cluster in sorted(cluster_to_doc_ids.keys()):
            cluster_docs = [documents[doc_id] for doc_id in cluster_to_doc_ids[cluster]]
            cluster_summaries = summaries[cluster]
            cluster_viewpoint = viewpoints[cluster]
            data = {
                'instance_id': cluster,
                'viewpoint': cluster_viewpoint,
                'documents': cluster_docs,
                'summaries': cluster_summaries
            }
            out.write(data)


def save_task4_abs_data(cluster_to_doc_ids: Dict[str, List[str]],
                        documents: Dict[str, List[str]],
                        summaries: Dict[str, List[List[str]]],
                        questions: Dict[str, Dict[str, Any]],
                        file_path: str) -> None:
    with JsonlWriter(file_path) as out:
        for cluster in sorted(cluster_to_doc_ids.keys()):
            cluster_docs = [documents[doc_id] for doc_id in cluster_to_doc_ids[cluster]]
            cluster_summaries = summaries[cluster]
            cluster_question = questions[cluster]
            assert len(cluster_summaries) == 4
            data = {
                'instance_id': cluster,
                'question': cluster_question,
                'documents': cluster_docs,
                'summaries': cluster_summaries
            }
            out.write(data)


def save_task4_ext_data(cluster_to_doc_ids: Dict[str, List[str]],
                        documents: Dict[str, List[str]],
                        summaries: Dict[str, List[List[Dict[str, Any]]]],
                        questions: Dict[str, Dict[str, Any]],
                        sentence_labels: Dict[str, List[Dict[str, Any]]],
                        file_path: str) -> None:
    with JsonlWriter(file_path) as out:
        for cluster in sorted(sentence_labels.keys()):
            doc_ids = list(cluster_to_doc_ids[cluster])
            doc_id_to_index = {doc_id: i for i, doc_id in enumerate(doc_ids)}

            cluster_docs = [documents[doc_id] for doc_id in doc_ids]
            cluster_summaries = summaries[cluster]
            cluster_question = questions[cluster]
            cluster_labels = sentence_labels[cluster]

            new_labels = []
            for label in cluster_labels:
                new_labels.append({
                    'doc_index': doc_id_to_index[label['filename']],
                    'sent_index': label['sent_index'],
                    'is_novel': label['is_novel']
                })

            data = {
                'instance_id': cluster,
                'question': cluster_question,
                'documents': cluster_docs,
                'summaries': cluster_summaries,
                'relevance_labels': new_labels
            }
            out.write(data)


def setup(data_root: str, output_dir: str) -> None:
    documents_tar = f'{data_root}/from-nist/DUC2003_Summarization_Documents.tgz'
    summaries_tar = f'{data_root}/scrapes/duc.nist.gov/past_duc/duc2003/results/manualsummaries/duc2003.manual.abstracts.tar.gz'
    main(documents_tar, summaries_tar, output_dir)


def main(documents_tar, summaries_tar, output_dir):
    sds, mds = load_summaries(summaries_tar)

    cluster_to_doc_ids, documents = load_task1_documents(documents_tar)
    save_task1_data(documents, sds, f'{output_dir}/task1.jsonl')

    cluster_to_doc_ids, documents = load_task2_documents(documents_tar)
    topics = load_task2_topics(documents_tar)
    save_task2_data(cluster_to_doc_ids, documents, mds, topics, f'{output_dir}/task2.jsonl')

    cluster_to_doc_ids, documents = load_task3_documents(documents_tar)
    viewpoints = load_task3_viewpoints(documents_tar)
    save_task3_data(cluster_to_doc_ids, documents, mds, viewpoints, f'{output_dir}/task3.jsonl')

    questions = load_task4_questions(documents_tar)
    cluster_to_doc_ids, abs_documents = load_task4_abstractive_documents(documents_tar)
    save_task4_abs_data(cluster_to_doc_ids, abs_documents, mds, questions, f'{output_dir}/task4.jsonl')

    cluster_to_doc_ids, ext_documents = load_task4_extractive_documents(documents_tar)
    sentence_labels = load_task4_sentence_labels(documents_tar)
    save_task4_ext_data(cluster_to_doc_ids, ext_documents, mds, questions, sentence_labels, f'{output_dir}/task4.sentence-labels.jsonl')


if __name__ == '__main__':
    argp = argparse.ArgumentParser()
    argp.add_argument('documents_tar')
    argp.add_argument('summaries_tar')
    argp.add_argument('output_dir')
    args = argp.parse_args()
    main(args)