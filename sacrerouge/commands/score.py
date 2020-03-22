import argparse
import json
from overrides import overrides
from tqdm import tqdm
from typing import Any, Dict, List

from sacrerouge.commands import Subcommand
from sacrerouge.common.util import merge_dict
from sacrerouge.io import JsonlReader, JsonlWriter
from sacrerouge.metrics import Metric, SummaryType


def load_metrics(config: Dict[str, Any]) -> List[Metric]:
    metrics = []
    for params in config['metrics']:
        metric = Metric.from_params(params)
        metrics.append(metric)
    return metrics


def score(metrics: List[Metric],
          summary: SummaryType,
          references: List[SummaryType],
          is_reference: bool) -> Dict[str, Any]:
    results = {}
    for metric in metrics:
        for name, value in metric.score(summary, references).items():
            if is_reference:
                name = name + '_jk'
            results[name] = value
    return results


def get_jackknifing_references_list(references: List[Any]) -> List[List[Any]]:
    jk_references_list = []
    for i in range(len(references)):
        jk_references_list.append(references[:i] + references[i + 1:])
    return jk_references_list


def average_jackknifing_metrics(metrics_list: List[Dict[str, Any]]) -> Dict[str, Any]:
    average = {}
    first = metrics_list[0]
    for key, value in first.items():
        if isinstance(value, dict):
            average[key] = average_jackknifing_metrics([metrics[key] for metrics in metrics_list])
        else:
            average[key] = sum(metrics[key] for metrics in metrics_list) / len(metrics_list)
    return average


def run_jackknifing(metrics: List[Metric], summary: SummaryType, references: List[SummaryType]) -> Dict[str, Any]:
    jk_references_list = get_jackknifing_references_list(references)
    results = {}
    for metric in metrics:
        # Compute the metrics for each jackknifing instance, then average
        # together for the final metrics
        jk_metrics_list = []
        for jk_references in jk_references_list:
            jk_metrics_list.append(metric.score(summary, jk_references))

        jk_metrics = average_jackknifing_metrics(jk_metrics_list)
        for name, value in jk_metrics.items():
            results[name + '_jk'] = value
    return results


class ScoreSubcommand(Subcommand):
    @overrides
    def add_subparser(self, parser: argparse._SubParsersAction):
        self.parser = parser.add_parser('score')
        self.parser.add_argument('summaries_jsonl')
        self.parser.add_argument('config')
        self.parser.add_argument('output_jsonl')
        self.parser.set_defaults(func=self.run)

    @overrides
    def run(self, args):
        config = json.load(open(args.config, 'r'))
        metrics = load_metrics(config)
        instances = JsonlReader(args.summaries_jsonl).read()

        with JsonlWriter(args.output_jsonl) as out:
            for instance in tqdm(instances):
                summarizer_type = instance['summarizer_type']
                summary = instance['summary']['text']
                references = [reference['text'] for reference in instance['references']]

                if summarizer_type == 'reference':
                    # No additional jackknifing needs to be done because the input
                    # for reference summaries is already "missing" a reference
                    # (i.e., itself), but the metric should be nammed the jackknifing version
                    results = score(metrics, summary, references, True)
                elif summarizer_type == 'peer':
                    # Score normally using all of the references
                    results = score(metrics, summary, references, False)

                    # Run jackknifing and combine results
                    jk_results = run_jackknifing(metrics, summary, references)
                    merge_dict(results, jk_results)
                else:
                    raise Exception(f'Unknown summarizer type: {summarizer_type}')

                out.write({'metrics': results})
