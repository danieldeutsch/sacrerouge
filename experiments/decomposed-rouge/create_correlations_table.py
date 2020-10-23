import argparse
import json
import os
from glob import glob
from typing import Dict


def load_correlations(input_dir: str, summarizer_type: str, level: str) -> Dict[str, Dict[str, float]]:
    correlations_dict = {}
    for input_file in glob(f'{input_dir}/*-{summarizer_type}.json'):
        name = os.path.basename(input_file)[:-len(f'-{summarizer_type}.json')]
        correlations = json.load(open(input_file, 'r'))
        correlations = correlations[level]
        correlations_dict[name] = {
            'pearson': correlations['pearson']['r'],
            'spearman': correlations['spearman']['rho'],
            'kendall': correlations['kendall']['tau'],
        }
    return correlations_dict


def main(args):
    correlations_dict = {}
    for name, input_dir in zip(args.dataset_names, args.correlation_dirs):
        correlations_dict[name] = load_correlations(input_dir, args.summarizer_type, args.correlation_level)
    metrics = sorted(list(correlations_dict.values())[0].keys())

    dirname = os.path.dirname(args.output_file)
    if dirname:
        os.makedirs(dirname, exist_ok=True)

    with open(args.output_file, 'w') as out:
        out.write('<table>\n')

        # Print the header with the dataset names
        out.write('<tr>\n')
        out.write('<th></th>\n')
        for dataset in args.dataset_names:
            out.write(f'<th colspan="3">{dataset}</th>\n')
        out.write('</tr>\n')

        # Print the header with the correlation coefficient names
        out.write('<tr>\n')
        out.write('<th></th>\n')
        for _ in args.dataset_names:
            for coef in ['r', 'p', 'k']:
                out.write(f'<th>{coef}</th>\n')
        out.write('</tr>\n')

        # Print each value in the table
        for metric in metrics:
            out.write('<tr>\n')
            out.write(f'<td>{metric}</td>\n')
            for dataset in args.dataset_names:
                out.write(f'<td>{correlations_dict[dataset][metric]["pearson"]:.2f}</td>\n')
                out.write(f'<td>{correlations_dict[dataset][metric]["spearman"]:.2f}</td>\n')
                out.write(f'<td>{correlations_dict[dataset][metric]["kendall"]:.2f}</td>\n')
            out.write('</tr>\n')

        out.write('</table>\n')

if __name__ == '__main__':
    argp = argparse.ArgumentParser()
    argp.add_argument('--dataset-names', nargs='+')
    argp.add_argument('--correlation-dirs', nargs='+')
    argp.add_argument('--output-file')
    argp.add_argument('--correlation-level', choices=['summary_level', 'system_level', 'global'])
    argp.add_argument('--summarizer-type', choices=['peer', 'reference', 'all'])
    args = argp.parse_args()
    main(args)