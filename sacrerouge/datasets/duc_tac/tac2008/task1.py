import argparse
import lxml.html
import re
import tarfile
from collections import namedtuple
from io import BytesIO
from lxml import etree
from nltk.tokenize import sent_tokenize
from typing import Dict

from sacrerouge.io import JsonlWriter

Document = namedtuple('Document', ['document_id', 'type', 'headline', 'date', 'text'])
Summary = namedtuple('Summary', ['annotator', 'text'])
Topic = namedtuple('Topic', ['title', 'narrative'])


class Instance(object):
    def __init__(self, cluster_id: str, selector: str):
        self.cluster_id = cluster_id
        self.selector = selector
        self.topic = None
        self.documents = []
        self.summaries = []


class UpdateInstance(object):
    def __init__(self, cluster_id: str, selector: str):
        self.cluster_id = cluster_id
        self.selector = selector
        self.topic = None
        self.documents_A = []
        self.documents_B = []
        self.summaries_A = []
        self.summaries_B = []


def parse_story(root):
    headline = None
    headline_nodes = list(root.xpath('body/doc/headline'))
    if len(headline_nodes) > 0:
        headline = headline_nodes[0].text_content().strip()

    text = []
    for p_node in root.xpath('body/doc/text/p'):
        paragraph = p_node.text_content().strip()
        paragraph = re.sub('\s+', ' ', paragraph)
        paragraph = sent_tokenize(paragraph)
        text.append(paragraph)

    return headline, text


def parse_other(root):
    # Everything is combined into a single paragraph.
    text = root.xpath('//text')[0].text_content().strip()
    text = re.sub('\s+', ' ', text)
    sentences = [sent_tokenize(text)]
    return sentences


def load_documents(documents_tar: str) -> Dict[str, UpdateInstance]:
    instances = {}

    with tarfile.open(documents_tar, 'r') as tar:
        inner_tar_bytes = tar.extractfile('TAC2008_Update_Summarization_Documents/UpdateSumm08_test_docs_files.tar.gz').read()
        with tarfile.open(fileobj=BytesIO(inner_tar_bytes)) as inner_tar:
            for member in inner_tar.getmembers():
                if member.isfile():
                    path = member.name.split('/')
                    cluster_id = path[1][:-1].lower()
                    selector = path[1][-1]
                    group = path[2][-1]
                    filename = path[-1]

                    if cluster_id not in instances:
                        instances[cluster_id] = UpdateInstance(cluster_id, selector)
                    instance = instances[cluster_id]

                    date = filename[8:16]
                    year, month, day = date[:4], date[4:6], date[6:]
                    date = f'{year}-{month}-{day}'

                    html = inner_tar.extractfile(member).read().decode()
                    tree = lxml.html.document_fromstring(html)

                    # The documents come from English Gigaword. Different document
                    # types have different structures, some of which we can parse
                    # ("story"), but others we cannot ("other")
                    document_type = tree.xpath('body/doc')[0].get('type')
                    if document_type == 'story':
                        headline, text = parse_story(tree)
                    else:
                        headline = None
                        text = parse_other(tree)

                    document = Document(filename, document_type, headline, date, text)
                    if group == 'A':
                        instance.documents_A.append(document)
                    else:
                        instance.documents_B.append(document)

    return instances


def load_summaries(instances: Dict[str, UpdateInstance], eval_tar: str) -> None:
    with tarfile.open(eval_tar, 'r') as tar:
        for member in tar.getmembers():
            if member.isfile() and member.name.startswith('UpdateSumm08_eval/ROUGE/models/'):
                path = member.name.split('/')
                filename = path[-1]
                parts = filename.split('.')
                cluster_id = parts[0].split('-')[0].lower()
                group = parts[0].split('-')[1]
                annotator = parts[4]

                instance = instances[cluster_id]

                sentences = tar.extractfile(member).read().decode().splitlines()
                sentences = list(filter(None, map(lambda sentence: sentence.strip(), sentences)))
                summary = Summary(annotator, sentences)

                if group == 'A':
                    instance.summaries_A.append(summary)
                else:
                    instance.summaries_B.append(summary)


def load_topics(instances: Dict[str, UpdateInstance], file_path: str) -> Dict[str, Topic]:
    topics = {}
    tree = etree.parse(file_path)
    for topic_node in tree.xpath('//topic'):
        cluster_id = topic_node.get('id')[:-1].lower()
        title = topic_node.xpath('title')[0].text.strip()
        narrative = sent_tokenize(topic_node.xpath('narrative')[0].text.strip())
        instances[cluster_id].topic = Topic(title, narrative)
    return topics


def save_instances(instances: Dict[str, UpdateInstance], output_dir: str) -> None:
    with JsonlWriter(f'{args.output_dir}/task1.jsonl') as out:
        with JsonlWriter(f'{args.output_dir}/task1.A.jsonl') as out_A:
            with JsonlWriter(f'{args.output_dir}/task1.B.jsonl') as out_B:
                for cluster_id in sorted(instances.keys()):
                    instance = instances[cluster_id]

                    instance_A = Instance(instance.cluster_id, instance.selector)
                    instance_A.topic = instance.topic
                    instance_A.documents = instance.documents_A
                    instance_A.summaries = instance.summaries_A

                    instance_B = Instance(instance.cluster_id, instance.selector)
                    instance_B.topic = instance.topic
                    instance_B.documents = instance.documents_B
                    instance_B.summaries = instance.summaries_B

                    out.write(instance)
                    out_A.write(instance_A)
                    out_B.write(instance_B)


def main(args):
    instances = load_documents(args.documents_tar)
    load_summaries(instances, args.eval_tar)
    load_topics(instances, args.topics_file)
    save_instances(instances, args.output_dir)


if __name__ == '__main__':
    argp = argparse.ArgumentParser()
    argp.add_argument('documents_tar')
    argp.add_argument('eval_tar')
    argp.add_argument('topics_file')
    argp.add_argument('output_dir')
    args = argp.parse_args()
    main(args)
