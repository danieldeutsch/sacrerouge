import tarfile
from collections import defaultdict
from typing import Set

from sacrerouge.io import JsonlWriter


def load_summaries(eval_tar_path: str):
    summaries = defaultdict(lambda: defaultdict(dict))
    reference_names = set()
    with tarfile.open(eval_tar_path, 'r') as tar:
        for member in tar.getmembers():
            if member.name.startswith('Evaluation_MultiLing2015_MSS/mss-submits/original/') and member.name.endswith('.txt'):
                path = member.name.split('/')
                summarizer_id = path[3] + '-' + path[5]
                language_code = path[4]
                instance_id = path[6][:-4]

                if summarizer_id.startswith('human'):
                    summarizer_type = 'reference'
                    reference_names.add(summarizer_id)
                else:
                    summarizer_type = 'peer'

                text = tar.extractfile(member).read().decode().splitlines()
                text = list(filter(None, [line.strip() for line in text]))
                if len(text) == 0:
                    continue

                summaries[language_code][instance_id][summarizer_id] = {
                    'summarizer_id': summarizer_id,
                    'summarizer_type': summarizer_type,
                    'text': text
                }
    return summaries, reference_names


def get_references(summaries, summarizer_id: str, reference_names: Set[str]):
    references = []
    for name in reference_names:
        if name == summarizer_id:
            continue
        references.append(summaries[name])
    return references


def save_data(summaries, reference_names, output_dir):
    for language in summaries.keys():
        with JsonlWriter(f'{output_dir}/{language}.summaries.jsonl') as out:
            for instance_id in sorted(summaries[language].keys()):
                for summarizer_id in sorted(summaries[language][instance_id].keys()):
                    summary = summaries[language][instance_id][summarizer_id]
                    references = get_references(summaries[language][instance_id], summarizer_id, reference_names)
                    if len(references) == 0:
                        continue
                    out.write({
                        'instance_id': instance_id,
                        'summarizer_id': summarizer_id,
                        'summarizer_type': summary['summarizer_type'],
                        'summary': summary,
                        'references': references
                    })


def setup(eval_tar_path: str, output_dir: str) -> None:
    summaries, reference_names = load_summaries(eval_tar_path)
    save_data(summaries, reference_names, output_dir)