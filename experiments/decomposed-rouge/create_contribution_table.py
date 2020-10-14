import argparse
import os
import sys
from typing import Dict

# Add sacrerouge to the path
sys.path.append('.')

from sacrerouge.data import Metrics
from sacrerouge.io import JsonlReader


def load_contributions(scores_jsonl: str) -> Dict[str, float]:
    metrics_dicts = []
    for metrics in JsonlReader(scores_jsonl, Metrics).read():
        if metrics.summarizer_type != 'peer':
            continue
        metrics_dicts.append(metrics.metrics)
    return sum(metrics_dicts) / len(metrics_dicts)


def main(args):
    contributions_dict = {}
    for name, input_jsonl in zip(args.dataset_names, args.score_jsonls):
        contributions_dict[name] = load_contributions(input_jsonl)
    metrics = sorted(list(contributions_dict.values())[0]['decomposed-rouge'].keys())
    metrics.remove('rouge-1')

    dirname = os.path.dirname(args.output_file)
    if dirname:
        os.makedirs(dirname, exist_ok=True)

    with open(args.output_file, 'w') as out:
        out.write('<table>\n')

        # Print the header with the dataset names
        out.write('<tr>\n')
        out.write('<th></th>\n')
        for dataset in args.dataset_names:
            out.write(f'<th>{dataset}</th>\n')
        out.write('</tr>\n')

        # Print each value in the table
        for metric in metrics:
            out.write('<tr>\n')
            out.write(f'<td>{metric}</td>\n')
            for dataset in args.dataset_names:
                out.write(f'<td>{contributions_dict[dataset]["decomposed-rouge"][metric]["coverage"]:.2f}</td>\n')
            out.write('</tr>\n')

        out.write('</table>\n')

if __name__ == '__main__':
    argp = argparse.ArgumentParser()
    argp.add_argument('--dataset-names', nargs='+')
    argp.add_argument('--score-jsonls', nargs='+')
    argp.add_argument('--output-file')
    args = argp.parse_args()
    main(args)