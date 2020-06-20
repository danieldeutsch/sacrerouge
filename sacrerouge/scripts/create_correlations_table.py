import argparse
import json
import os
from collections import defaultdict


def get_datasets(args):
    datasets = []
    for _, _, dataset in args.input:
        if dataset not in datasets:
            datasets.append(dataset)
    return datasets


def get_metrics(args):
    metrics = []
    for _, metric, _ in args.input:
        if metric not in metrics:
            metrics.append(metric)
    return metrics


def main(args):
    datasets = get_datasets(args)
    metrics = get_metrics(args)

    values = defaultdict(dict)
    for file_path, metric, dataset in args.input:
        correlations = json.load(open(file_path, 'r'))
        values[metric][dataset] = correlations

    dirname = os.path.dirname(args.output_file)
    if dirname:
        os.makedirs(dirname, exist_ok=True)

    with open(args.output_file, 'w') as out:
        out.write('<table>\n')

        # Print the header with the dataset names
        out.write('<tr>\n')
        out.write('<th></th>\n')
        for dataset in datasets:
            out.write(f'<th colspan="3">{dataset}</th>\n')
        out.write('</tr>\n')

        # Print the header with the correlation coefficient names
        out.write('<tr>\n')
        out.write('<th></th>\n')
        for dataset in datasets:
            for coef in ['r', 'p', 'k']:
                out.write(f'<th>{coef}</th>\n')
        out.write('</tr>\n')

        # Print each value in the table
        for metric in metrics:
            out.write('<tr>\n')
            out.write(f'<td>{metric}</td>\n')
            for dataset in datasets:
                out.write(f'<td>{values[metric][dataset][args.correlation_level]["pearson"]["r"]:.2f}</td>\n')
                out.write(f'<td>{values[metric][dataset][args.correlation_level]["spearman"]["rho"]:.2f}</td>\n')
                out.write(f'<td>{values[metric][dataset][args.correlation_level]["kendall"]["tau"]:.2f}</td>\n')
            out.write('</tr>\n')

        out.write('</table>\n')


if __name__ == '__main__':
    argp = argparse.ArgumentParser()
    argp.add_argument('output_file')
    argp.add_argument('correlation_level', choices=['summary_level', 'system_level', 'global'])
    argp.add_argument('--input', action='append', nargs=3, metavar=('file_path', 'metric', 'dataset'))
    args = argp.parse_args()
    main(args)