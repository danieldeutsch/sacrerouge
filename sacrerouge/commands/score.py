import argparse
import jsons
from collections import defaultdict
from overrides import overrides
from tqdm import tqdm
from typing import Any, Dict, List

from sacrerouge.commands import Subcommand
from sacrerouge.data import EvalInstance, Metrics
from sacrerouge.data.dataset_readers import DatasetReader
from sacrerouge.io import JsonlWriter
from sacrerouge.metrics import Metric


def _load_metrics(config: Dict[str, Any]) -> List[Metric]:
    metrics = []
    for params in config['metrics']:
        metric = Metric.from_params(params)
        metrics.append(metric)
    return metrics


def _score_with_metric(metric: Metric,
                      instances: List[EvalInstance],
                      metrics_dicts: Dict[str, Dict[str, Metrics]]) -> None:
    fields_list = []
    field_to_index = {}
    instances_list = []
    jackknifing_flags = []

    for instance in instances:
        # Select just the relevant fields for this metric
        fields = instance.fields.select_fields(metric.required_fields)

        # Score the instance normally using all of the fields. However,
        # if the metric requires jackknifing and this is a reference summary,
        # the metric is comparable to the jackknifing metrics.
        is_jackknifing = metric.requires_jackknifing() and instance.summarizer_type == 'reference'

        if fields not in field_to_index:
            field_to_index[fields] = len(field_to_index)
            fields_list.append(fields)
            instances_list.append([])
            jackknifing_flags.append([])

        index = field_to_index[fields]
        instances_list[index].append(instance)
        jackknifing_flags[index].append(is_jackknifing)

        # Potentially run jackknifing for the peers
        if metric.requires_jackknifing() and instance.summarizer_type == 'peer':
            jk_fields_list = metric.jackknifer.get_jackknifing_fields_list(fields)
            if jk_fields_list:
                for jk_fields in jk_fields_list:
                    if jk_fields not in field_to_index:
                        field_to_index[jk_fields] = len(field_to_index)
                        fields_list.append(jk_fields)
                        instances_list.append([])
                        jackknifing_flags.append([])

                    index = field_to_index[jk_fields]
                    instances_list[index].append(instance)
                    jackknifing_flags[index].append(True)

    # Score the summaries
    summaries_lists = [[instance.summary for instance in instances] for instances in instances_list]
    args = [[fields[name] for fields in fields_list] for name in metric.required_fields]
    results_lists = metric.score_multi_all(summaries_lists, *args)

    # Used to aggregate the jk results
    jk_results = defaultdict(lambda: defaultdict(list))

    for i, results_list in enumerate(results_lists):
        for j, results in enumerate(results_list):
            instance = instances_list[i][j]
            is_jackknifing = jackknifing_flags[i][j]
            if is_jackknifing:
                jk_results[instance.instance_id][instance.summarizer_id].append(results)
            else:
                metrics_dicts[instance.instance_id][instance.summarizer_id].metrics.update(results)

    # Aggregate the jk results
    for instance_id in jk_results.keys():
        for summarizer_id, results in jk_results[instance_id].items():
            result = sum(results) / len(results)
            for name, value in result.items():
                metrics_dicts[instance_id][summarizer_id].metrics[name + '_jk'] = value


def _get_initial_metrics_dicts(instances: List[EvalInstance]) -> Dict[str, Dict[str, Metrics]]:
    metrics_dicts = defaultdict(dict)
    for instance in instances:
        metrics = Metrics(instance.instance_id, instance.summarizer_id, instance.summarizer_type)
        metrics_dicts[instance.instance_id][instance.summarizer_id] = metrics
    return metrics_dicts


def score_instances(instances: List[EvalInstance], metrics: List[Metric]) -> Dict[str, Dict[str, Metrics]]:
    metrics_dicts = _get_initial_metrics_dicts(instances)
    for metric in metrics:
        _score_with_metric(metric, instances, metrics_dicts)
    return metrics_dicts


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
        metrics = _load_metrics(config)

        instances = dataset_reader.read()
        metrics_dicts = score_instances(instances, metrics)

        # Save the results to the output file
        with JsonlWriter(args.output_jsonl) as out:
            for instance_id in sorted(metrics_dicts.keys()):
                for summarizer_id in sorted(metrics_dicts[instance_id].keys()):
                    out.write(metrics_dicts[instance_id][summarizer_id])
