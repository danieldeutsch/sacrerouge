import argparse
from collections import defaultdict
from overrides import overrides
from typing import Dict, List
import inspect
import sys

from sacrerouge.commands import Subcommand
from sacrerouge.common import Params
from sacrerouge.data import EvalInstance, Metrics
from sacrerouge.data.dataset_readers import DatasetReader
from sacrerouge.io import JsonlWriter
from sacrerouge.metrics import Metric
from sacrerouge.data.dataset_readers import *
from sacrerouge.metrics import *


def _load_metrics(params: Params) -> List[Metric]:
    metrics = []
    for metric_params in params.pop('metrics'):
        metric = Metric.from_params(metric_params)
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
    def __init__(self, cr, command_prefix):
        super().__init__()
        sub_prefix = command_prefix + ['score']
        dataset_reader_command_args_lookup = dict()
        #dataset_reader_defaults_lookup = dict()
        for dataset_reader_name, dataset_reader_class in DatasetReader._registry.items():
            if issubclass(dataset_reader_class, DatasetReader):
                argspec = inspect.getfullargspec(dataset_reader_class.__init__)
                args = argspec.args[1:]
                #defaults = list(argspec.defaults) if argspec.defaults is not None else None
                annotations = argspec.annotations
                dataset_reader_command_args = []
                for i in range(0, len(args)):
                    dataset_reader_command_args.append({"name": args[i]})
                dataset_reader_command_args_lookup[dataset_reader_name] = dataset_reader_command_args

        for metric_name, metric_class in Metric._registry.items():
            if issubclass(metric_class, Metric):
                argspec = inspect.getfullargspec(metric_class.__init__)
                args = argspec.args[1:]
                defaults = list(argspec.defaults)
                defaults_dict = dict()
                annotations = argspec.annotations
                command_args = []
                for i in range(0, len(args)):
                    arg_name = args[i]
                    if arg_name == "jackknifer":
                        continue
                    default_value = defaults[i]
                    defaults_dict[arg_name] = defaults[i]
                    command_args.append({"name": "--" + arg_name, "default": default_value})
                command_args.append({"name": "output_jsonl"})
                command_args.append({"name": "--overrides"})
                for dataset_reader_name in dataset_reader_command_args_lookup.keys():
                    defaults_dict["metric"] = metric_name
                    defaults_dict["dataset_reader"] = dataset_reader_name
                    cr.register_command(sub_prefix + [metric_name, dataset_reader_name], dataset_reader_command_args_lookup[dataset_reader_name] + command_args, self.run, defaults = defaults_dict)

    @overrides
    def run(self, args):
        def dataset_reader_name(dataset_reader):
            return ''.join(x.title() for x in dataset_reader.split('_')) + 'DatasetReader'
        def metric_name(metric):
            return ''.join(x.title() if len(x) > 2 else x.upper() for x in metric.split('_'))

        def construct(cls, args):
            print(cls)
            argspec = inspect.getfullargspec(cls.__init__)
            args_list = argspec.args[1:]
            args_dict = vars(args)
            params = dict()
            for arg_name in args_list:
                params[arg_name] = args_dict[arg_name]
            print(params)
            return cls(**params)

        dataset_reader_cls_name = args.dataset_reader.replace('-', '_')
        dataset_reader_cls = getattr(sys.modules[__name__], dataset_reader_name(dataset_reader_cls_name))
        metric_cls_name = args.metric.replace('-', '_')
        metric_cls = getattr(sys.modules[__name__], metric_name(metric_cls_name))
        dataset_reader = construct(dataset_reader_cls, args)
        metric = construct(metric_cls, args)
        metrics = [metric]

        instances = dataset_reader.read()
        metrics_dicts = score_instances(instances, metrics)

        # Save the results to the output file
        with JsonlWriter(args.output_jsonl) as out:
            for instance_id in sorted(metrics_dicts.keys()):
                for summarizer_id in sorted(metrics_dicts[instance_id].keys()):
                    out.write(metrics_dicts[instance_id][summarizer_id])
