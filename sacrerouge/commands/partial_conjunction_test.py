import argparse
import json
import logging
import os
from collections import defaultdict
from overrides import overrides
from typing import Dict, List,  Union

from sacrerouge.commands import RootSubcommand
from sacrerouge.common.logging import prepare_global_logging
from sacrerouge.stats import partial_conjunction_pvalue_test

logger = logging.getLogger(__name__)


def load_pvalue_dicts(pvalue_json_files_or_dicts: Union[List[str], List[Dict]],
                      names: List[str]) -> Dict[str, Dict[str, Dict[str, float]]]:
    assert len(pvalue_json_files_or_dicts) == len(names)
    pvalues_list = []
    for json_file_or_dict in pvalue_json_files_or_dicts:
        if isinstance(json_file_or_dict, str):
            pvalues = json.load(open(json_file_or_dict, 'r'))
        else:
            pvalues = json_file_or_dict
        pvalues_list.append(pvalues)

    # Ensure they all have the same levels
    levels = set()
    for level in ['summary_level', 'system_level', 'global']:
        if level in pvalues_list[0]:
            levels.add(level)
    for pvalues in pvalues_list:
        for level in levels:
            assert level in pvalues

    pvalue_dict = defaultdict(lambda: defaultdict(dict))
    for name, pvalues in zip(names, pvalues_list):
        for level in levels:
            for coef in ['pearson', 'spearman', 'kendall']:
                pvalue_dict[level][name][coef] = pvalues[level][coef]['pvalue']
    return pvalue_dict


def run_partial_conjunction_pvalue_test(method: str,
                                        pvalues_dict: Dict[str, Dict[str, float]],
                                        alpha: float = 0.05) -> float:
    results = {}
    for coef in ['pearson', 'spearman', 'kendall']:
        metrics = []
        pvalues = []
        for metric, ps in pvalues_dict.items():
            metrics.append(metric)
            pvalues.append(ps[coef])

        k, significant_indices = partial_conjunction_pvalue_test(method, pvalues, alpha=alpha)
        significant_metrics = [metrics[i] for i in significant_indices]
        results[coef] = {
            'k': k,
            'significant': significant_metrics
        }
    return results


def run_all_partial_conjunction_pvalue_test(method: str,
                                            pvalue_json_files_or_dicts: Union[List[str], List[Dict]],
                                            names: List[str],
                                            alpha: float = 0.05) -> Dict:
    pvalue_dict = load_pvalue_dicts(pvalue_json_files_or_dicts, names)
    results = {
        'method': method,
        'names': names,
        'alpha': alpha
    }
    for level in pvalue_dict.keys():
        results[level] = run_partial_conjunction_pvalue_test(method, pvalue_dict[level], alpha=alpha)
    return results


@RootSubcommand.register('partial-conjunction-test')
class PartialConjunctionTestSubcommand(RootSubcommand):
    @overrides
    def add_subparser(self, parser: argparse._SubParsersAction):
        description = 'Run a partial conjunction test on a set of p-values'
        self.parser = parser.add_parser('partial-conjunction-test', description=description, help=description)
        self.parser.add_argument(
            '--pvalue-json-files',
            nargs='+',
            help='The json files with the p-values to run the partial conjunction p-value test on',
            required=True
        )
        self.parser.add_argument(
            '--names',
            nargs='+',
            type=str,
            help='The names for the correspond pvalue json files',
            required=True
        )
        self.parser.add_argument(
            '--method',
            choices=['bonferroni'],
            default='bonferroni',
            help='The partial conjunction p-value method to use'
        )
        self.parser.add_argument(
            '--alpha',
            type=float,
            default=0.05,
            help='The signifiance level of the test'
        )
        self.parser.add_argument(
            '--output-file',
            type=str,
            help='The json output file which will contain the final correlations'
        )
        self.parser.add_argument(
            '--log-file',
            type=str,
            help='The file where the log should be written'
        )
        self.parser.add_argument(
            '--silent',
            action='store_true',
            help='Controls whether the log should be written to stdout'
        )
        self.parser.set_defaults(func=self.run)

    def run(self, args):
        prepare_global_logging(file_path=args.log_file, silent=args.silent)

        results = run_all_partial_conjunction_pvalue_test(args.method, args.pvalue_json_files, args.names,
                                                          alpha=args.alpha)

        if args.output_file:
            dirname = os.path.dirname(args.output_file)
            if dirname:
                os.makedirs(dirname, exist_ok=True)
            with open(args.output_file, 'w') as out:
                out.write(json.dumps(results, indent=2))

        if not args.silent:
            logger.info(json.dumps(results, indent=2))