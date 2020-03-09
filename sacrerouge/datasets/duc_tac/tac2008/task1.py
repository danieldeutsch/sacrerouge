import argparse
import lxml.html
import re
import tarfile
from collections import defaultdict
from io import BytesIO
from lxml import etree
from nltk.tokenize import sent_tokenize

from sacrerouge.io import JsonlWriter


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


def load_documents(documents_tar: str):
    selectors = {}
    documents = defaultdict(lambda: defaultdict(list))

    with tarfile.open(documents_tar, 'r') as tar:
        inner_tar_bytes = tar.extractfile('TAC2008_Update_Summarization_Documents/UpdateSumm08_test_docs_files.tar.gz').read()
        with tarfile.open(fileobj=BytesIO(inner_tar_bytes)) as inner_tar:
            for member in inner_tar.getmembers():
                if member.isfile():
                    path = member.name.split('/')
                    instance_id = path[1][:-1].lower()
                    selector = path[1][-1]
                    group = path[2][-1]
                    filename = path[-1]

                    if instance_id not in selectors:
                        selectors[instance_id] = selector

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

                    document = {
                        'filename': filename,
                        'document_type': document_type,
                        'headline': headline,
                        'date': date,
                        'text': text
                    }
                    documents[instance_id][group].append(document)

    return documents, selectors


def load_summaries(eval_tar: str) -> None:
    summaries = defaultdict(lambda: defaultdict(list))
    with tarfile.open(eval_tar, 'r') as tar:
        for member in tar.getmembers():
            if member.isfile() and member.name.startswith('UpdateSumm08_eval/ROUGE/models/'):
                path = member.name.split('/')
                filename = path[-1]
                parts = filename.split('.')
                instance_id = parts[0].split('-')[0].lower()
                group = parts[0].split('-')[1]
                annotator = parts[4]

                sentences = tar.extractfile(member).read().decode().splitlines()
                sentences = list(filter(None, map(lambda sentence: sentence.strip(), sentences)))
                summary = {
                    'annotator': annotator,
                    'text': sentences
                }
                summaries[instance_id][group].append(summary)
    return summaries


def load_topics(file_path: str):
    topics = {}
    tree = etree.parse(file_path)
    for topic_node in tree.xpath('//topic'):
        instance_id = topic_node.get('id')[:-1].lower()
        title = topic_node.xpath('title')[0].text.strip()
        narrative = sent_tokenize(topic_node.xpath('narrative')[0].text.strip())
        topics[instance_id] = {
            'title': title,
            'narrative': narrative
        }
    return topics


def save_instances(documents, selectors, summaries, topics, output_dir: str) -> None:
    with JsonlWriter(f'{args.output_dir}/task1.A-B.jsonl') as out_A_B:
        with JsonlWriter(f'{args.output_dir}/task1.A.jsonl') as out_A:
            with JsonlWriter(f'{args.output_dir}/task1.B.jsonl') as out_B:
                for instance_id in sorted(documents.keys()):
                    topic = topics[instance_id]
                    selector = selectors[instance_id]

                    documents_A = documents[instance_id]['A']
                    documents_B = documents[instance_id]['B']

                    summaries_A = summaries[instance_id]['A']
                    summaries_B = summaries[instance_id]['B']

                    out_A.write({
                        'instance_id': f'{instance_id}-A',
                        'selector': selector,
                        'topic': topic,
                        'documents': documents_A,
                        'summaries': summaries_A
                    })
                    out_B.write({
                        'instance_id': f'{instance_id}-B',
                        'selector': selector,
                        'topic': topic,
                        'documents': documents_B,
                        'summaries': summaries_B
                    })
                    out_A_B.write({
                        'instance_id': instance_id,
                        'selector': selector,
                        'topic': topic,
                        'documents_A': documents_A,
                        'documents_B': documents_B,
                        'summaries_A': summaries_A,
                        'summaries_B': summaries_B
                    })


def main(args):
    documents, selectors = load_documents(args.documents_tar)
    summaries = load_summaries(args.eval_tar)
    topics = load_topics(args.topics_file)
    save_instances(documents, selectors, summaries, topics, args.output_dir)


if __name__ == '__main__':
    argp = argparse.ArgumentParser()
    argp.add_argument('documents_tar')
    argp.add_argument('eval_tar')
    argp.add_argument('topics_file')
    argp.add_argument('output_dir')
    args = argp.parse_args()
    main(args)
