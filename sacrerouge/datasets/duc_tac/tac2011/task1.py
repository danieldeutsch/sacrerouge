import gzip
import lxml.html
import re
import tarfile
from collections import defaultdict
from io import BytesIO
from nltk.tokenize import sent_tokenize
from tqdm import tqdm
from typing import Dict, List

from sacrerouge.io import JsonlWriter

_CATEGORIES = [
    'Accidents and Natural Disasters',
    'Attacks',
    'Health and Safety',
    'Endangered Resources',
    'Investigations and Trials'
]


def load_clusters_and_topics(file_path: str):
    clusters = defaultdict(lambda: defaultdict(list))
    topics = {}
    # There is something weird that lxml does not like about the first
    # 35 lines, so we remove them
    html = open(file_path, 'r').read().splitlines()
    html = ' '.join(html[36:])
    tree = lxml.html.document_fromstring(html)
    for topic_node in tree.xpath('//topic'):
        cluster = topic_node.get('id')[:-1].lower()
        category = _CATEGORIES[int(topic_node.get('category').strip()) - 1]
        title = topic_node.xpath('title')[0].text.strip()
        topics[cluster] = {
            'title': title,
            'category': category
        }

        for doc_node in topic_node.xpath('docseta/doc'):
            # Get the filename by stripping off the LDC ID
            file_id = doc_node.get('id')
            filename = file_id[:-11]
            clusters[cluster]['A'].append(filename)

        for doc_node in topic_node.xpath('docsetb/doc'):
            # Get the filename by stripping off the LDC ID
            file_id = doc_node.get('id')
            filename = file_id[:-11]
            clusters[cluster]['B'].append(filename)

    return clusters, topics


def parse_story(doc_node):
    headline = None
    headline_nodes = list(doc_node.xpath(f'./headline'))
    if len(headline_nodes) > 0:
        headline = headline_nodes[0].text_content().strip()

    text = []
    for p_node in doc_node.xpath('./text/p'):
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


def load_documents(gigaword_root: str, clusters: Dict[str, List[str]]):
    document_set = set()
    for groups in clusters.values():
        for documents in groups.values():
            for document in documents:
                document_set.add(document)

    documents = {}
    for document_id in tqdm(document_set):
        tqdm.write(document_id)

        corpus = document_id[:7].lower()
        gzip_name = document_id[:14].lower()
        file_path = f'{gigaword_root}/data/{corpus}/{gzip_name}.gz'

        date = document_id[8:16]
        year, month, day = date[:4], date[4:6], date[6:]
        date = f'{year}-{month}-{day}'

        html = gzip.open(file_path, 'rb').read().decode()
        tree = lxml.html.document_fromstring(html)

        doc_node = tree.xpath(f"body/doc[@id='{document_id}']")[0]

        # The documents come from English Gigaword. Different document
        # types have different structures, some of which we can parse
        # ("story"), but others we cannot ("other")
        document_type = tree.xpath('body/doc')[0].get('type')
        if document_type == 'story':
            headline, text = parse_story(doc_node)
        else:
            headline = None
            text = parse_other(doc_node)

        document = {
            'filename': document_id,
            'document_type': document_type,
            'headline': headline,
            'date': date,
            'text': text
        }
        documents[document_id] = document

    return documents


def load_summaries(eval_tar: str):
    summaries = defaultdict(lambda: defaultdict(list))
    with tarfile.open(eval_tar, 'r') as tar:
        for member in tar.getmembers():
            if member.isfile() and member.name.startswith('GuidedSumm2011_eval/ROUGE/models/'):
                path = member.name.split('/')
                filename = path[-1]
                parts = filename.split('.')
                instance_id = parts[0].split('-')[0].lower()
                group = parts[0].split('-')[1]
                annotator = parts[4]

                sentences = tar.extractfile(member).read().decode(errors='replace').strip().splitlines()
                sentences = list(map(lambda sent: sent.strip(), sentences))
                summary = {
                    'annotator': annotator,
                    'text': sentences
                }
                summaries[instance_id][group].append(summary)
    return summaries


def save_instances(clusters, documents, summaries, topics, output_dir: str) -> None:
    with JsonlWriter(f'{output_dir}/task1.A-B.jsonl') as out_A_B:
        with JsonlWriter(f'{output_dir}/task1.A.jsonl') as out_A:
            with JsonlWriter(f'{output_dir}/task1.B.jsonl') as out_B:
                for instance_id in clusters.keys():
                    topic = topics[instance_id]

                    documents_A = [documents[file_id] for file_id in clusters[instance_id]['A']]
                    documents_B = [documents[file_id] for file_id in clusters[instance_id]['B']]

                    summaries_A = summaries[instance_id]['A']
                    summaries_B = summaries[instance_id]['B']

                    out_A.write({
                        'instance_id': f'{instance_id}-A',
                        'topic': topic,
                        'documents': documents_A,
                        'summaries': summaries_A
                    })
                    out_B.write({
                        'instance_id': f'{instance_id}-B',
                        'topic': topic,
                        'documents': documents_B,
                        'summaries': summaries_B
                    })
                    out_A_B.write({
                        'instance_id': instance_id,
                        'topic': topic,
                        'documents_A': documents_A,
                        'documents_B': documents_B,
                        'summaries_A': summaries_A,
                        'summaries_B': summaries_B
                    })


def setup(gigaword_root: str, data_root: str, output_dir: str):
    eval_tar = f'{data_root}/scrapes/tac.nist.gov/protected/past/2011/GuidedSumm2011_eval.tgz'
    topics_file = f'{data_root}/scrapes/tac.nist.gov/protected/past/2011/GuidedSumm11_test_topics.xml.txt'
    main(gigaword_root, eval_tar, topics_file, output_dir)


def main(gigaword_root, eval_tar, topics_file, output_dir):
    clusters, topics = load_clusters_and_topics(topics_file)
    documents = load_documents(gigaword_root, clusters)
    summaries = load_summaries(eval_tar)
    save_instances(clusters, documents, summaries, topics, output_dir)