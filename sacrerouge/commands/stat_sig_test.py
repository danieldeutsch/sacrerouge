import argparse
import json
import logging
import os
import scipy.stats
from overrides import overrides
from typing import Any, Dict, Tuple

from sacrerouge.commands import Subcommand
from sacrerouge.common.logging import prepare_global_logging


logger = logging.getLogger(__name__)


def _get_equations(alternative: str) -> Tuple[str, str]:
    # Returns the equations for the null and alternative hypotheses based on the description in
    # https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.wilcoxon.html
    if alternative == 'two-sided':
        return 'A = B', 'A != B'
    if alternative == 'greater':
        return 'A < B', 'A > B'
    if alternative == 'less':
        return 'A > B', 'A < B'
    raise Exception(f'Unknown alternative: {alternative}')


def run_wilcoxon_tests(correlations_A: Dict[str, Dict[str, float]],
                       correlations_B: Dict[str, Dict[str, float]],
                       alternative: str = 'two-sided') -> Dict[str, Any]:
    null_eq, alternative_eq = _get_equations(alternative)
    results = {
        'alternative': alternative,
        'null_equation': null_eq,
        'alternative_equation': alternative_eq
    }

    coefficients = set(correlations_A.keys()) & set(correlations_B.keys())
    for coef in coefficients:
        logger.info(f'Running Wilcoxon test on the {coef} summary-level correlations')

        instance_ids = set(correlations_A[coef].keys()) & set(correlations_B[coef].keys())
        logger.info(f'Found {len(instance_ids)} common instance correlations')

        values_A = []
        values_B = []
        for instance_id in instance_ids:
            values_A.append(correlations_A[coef][instance_id])
            values_B.append(correlations_B[coef][instance_id])

        statistic, p_value = scipy.stats.wilcoxon(values_A, values_B, alternative=alternative)
        results[coef] = {'statistic': statistic, 'p_value': p_value, 'n': len(values_A)}

        logger.info(f'Test statistic: {statistic}, p-value: {p_value}')

    return results


class StatisticalSignificanceTestSubcommand(Subcommand):
    @overrides
    def add_subparser(self, parser: argparse._SubParsersAction):
        description = 'Run a Wilcoxon signed-rank test on two sets of summary-level correlations'
        self.parser = parser.add_parser('stat-sig-test', description=description, help=description)
        self.parser.add_argument(
            '--summary-level-correlations-A',
            type=str,
            help='The individual summary-level correlations for metric A',
            required=True
        )
        self.parser.add_argument(
            '--summary-level-correlations-B',
            type=str,
            help='The individual summary-level correlations for metric B',
            required=True
        )
        self.parser.add_argument(
            '--output-file',
            type=str,
            help='The json output file which will contain the test results'
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
        self.parser.add_argument(
            '--alternative',
            type=str,
            choices=['two-sided', 'greater', 'less'],
            default='two-sided',
            help='The alternative hypothesis for the test. See https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.wilcoxon.html for details'
        )
        self.parser.set_defaults(func=self.run)

    def run(self, args):
        prepare_global_logging(file_path=args.log_file, silent=args.silent)

        correlations_A = json.load(open(args.summary_level_correlations_A, 'r'))
        correlations_B = json.load(open(args.summary_level_correlations_B, 'r'))

        results = run_wilcoxon_tests(correlations_A, correlations_B, alternative=args.alternative)

        if args.output_file:
            dirname = os.path.dirname(args.output_file)
            if dirname:
                os.makedirs(dirname, exist_ok=True)
            with open(args.output_file, 'w') as out:
                out.write(json.dumps(results, indent=2))

        if not args.silent:
            logger.info(json.dumps(results, indent=2))