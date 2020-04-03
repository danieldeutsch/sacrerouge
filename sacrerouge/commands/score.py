import argparse
import jsons
from overrides import overrides
from tqdm import tqdm
from typing import Any, Dict, List

from sacrerouge.commands import Subcommand
from sacrerouge.data import EvalInstance, Metrics
from sacrerouge.data.dataset_readers import DatasetReader
from sacrerouge.io import JsonlWriter
from sacrerouge.metrics import Metric


def load_metrics(config: Dict[str, Any]) -> List[Metric]:
    metrics = []
    for params in config['metrics']:
        metric = Metric.from_params(params)
        metrics.append(metric)
    return metrics


def score(metric: Metric,
          instance: EvalInstance,
          is_jackknifing: bool,
          metrics_dict: Metrics) -> None:
    summary = instance.summary
    args = [instance.fields[field] for field in metric.required_fields]
    for name, value in metric.score(summary, *args).items():
        if is_jackknifing:
            name = name + '_jk'
        metrics_dict.metrics[name] = value


def maybe_run_jackknifing(metric: Metric,
                          instance: EvalInstance,
                          metrics_dict: Metrics) -> None:
    # We only do jackknifing if this metric requires it and it's possible to do
    if metric.requires_jackknifing():
        jk_fields_list = metric.jackknifer.get_jackknifing_fields_list(instance.fields)
        if jk_fields_list:
            results_list = []
            for jk_fields in jk_fields_list:
                args = [jk_fields[field] for field in metric.required_fields]
                results_list.append(metric.score(instance.summary, *args))
            results = sum(results_list) / len(results_list)
            for name, value in results.items():
                metrics_dict.metrics[name + '_jk'] = value


def get_initial_metrics_list(instances: List[EvalInstance]) -> List[Metrics]:
    metrics_list = []
    for instance in instances:
        metrics_list.append(Metrics(instance.instance_id, instance.summarizer_id, instance.summarizer_type))
    return metrics_list


class ScoreSubcommand(Subcommand):
    @overrides
    def add_subparser(self, parser: argparse._SubParsersAction):
        self.parser = parser.add_parser('score')
        self.parser.add_argument('config')
        self.parser.add_argument('output_jsonl')
        self.parser.set_defaults(func=self.run)

    @overrides
    def run(self, args):
        config = jsons.loads(open(args.config, 'r').read())
        dataset_reader = DatasetReader.from_params(config['dataset_reader'])
        metrics = load_metrics(config)

        instances = dataset_reader.read()
        metrics_list = get_initial_metrics_list(instances)

        for metric in tqdm(metrics):
            for i, instance in enumerate(tqdm(instances)):
                summarizer_type = instance.summarizer_type

                if summarizer_type == 'reference':
                    # There is no jackknifing to be done, but if this metric
                    # requires jackknifing, we want to indicate that this calcuation
                    # is comparable to jackknifed result
                    is_jackknifing = metric.requires_jackknifing()
                    score(metric, instance, is_jackknifing, metrics_list[i])
                elif summarizer_type == 'peer':
                    # Score normally using all of the references
                    score(metric, instance, False, metrics_list[i])

                    # Run jackknifing
                    maybe_run_jackknifing(metric, instance, metrics_list[i])
                else:
                    raise Exception(f'Unknown summarizer type: {summarizer_type}')

        # Save the results to the output file
        with JsonlWriter(args.output_jsonl) as out:
            for metrics in metrics_list:
                out.write(metrics)
