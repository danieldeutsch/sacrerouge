import tarfile
from collections import defaultdict
from nltk.tokenize import sent_tokenize

from sacrerouge.io import JsonlWriter


def load_reference_summaries(eval_path: str):
    summaries = defaultdict(dict)
    with tarfile.open(eval_path, 'r') as tar:
        for member in tar.getmembers():
            if member.name.startswith('Evaluation/2017_summaries/') and member.name.endswith('.txt'):
                if 'simple' in member.name:
                    # Seems to be a dummy language
                    continue
                path = member.name.split('/')
                language_code = path[2]
                instance_id = path[3][:32]
                text = tar.extractfile(member).read().decode().splitlines()
                if language_code == 'en':
                    text = [sent_tokenize(paragraph) for paragraph in text]
                summaries[language_code][instance_id] = {
                    'summarizer_id': 'reference',
                    'summarizer_type': 'reference',
                    'text': text
                }
    return summaries


def load_peer_summaries(eval_path: str):
    summaries = defaultdict(lambda: defaultdict(dict))
    with tarfile.open(eval_path, 'r') as tar:
        for member in tar.getmembers():
            if member.name.startswith('Evaluation/MultiLing17_Submissions') and member.name.endswith('.txt'):
                path = member.name.split('/')
                if path[2] == 'baselines2017':
                    if member.name.endswith('_body.txt'):
                        # Skip the "body" baseline"
                        continue
                    summarizer_id = path[3]
                    if summarizer_id == '2017_summaries':
                        # These are the references again
                        continue
                    language = path[4]
                    if language == 'simple':
                        continue

                    instance_id = path[5][:32]
                else:
                    summarizer_id = path[2] + '-' + path[3]
                    language = path[4]
                    instance_id = path[5][:32]

                text = tar.extractfile(member).read().decode().splitlines()
                if language == 'en':
                    text = [sent_tokenize(paragraph) for paragraph in text]
                summaries[language][instance_id][summarizer_id] = {
                    'summarizer_id': summarizer_id,
                    'summarizer_type': 'peer',
                    'text': text
                }
    return summaries


def save_data(references, peers, output_dir):
    for language in references.keys():
        with JsonlWriter(f'{output_dir}/{language}.summaries.jsonl') as out:
            for instance_id in sorted(references[language].keys()):
                for summarizer_id in sorted(peers[language][instance_id].keys()):
                    summary = peers[language][instance_id][summarizer_id]
                    out.write({
                        'instance_id': instance_id,
                        'summarizer_id': summarizer_id,
                        'summarizer_type': summary['summarizer_type'],
                        'summary': summary,
                        'references': [references[language][instance_id]]
                    })


def setup(eval_path: str, output_dir: str):
    references = load_reference_summaries(eval_path)
    peers = load_peer_summaries(eval_path)
    save_data(references, peers, output_dir)