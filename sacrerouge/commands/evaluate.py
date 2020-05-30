import argparse
import jsons
import os
from overrides import overrides
from typing import List
import inspect
import sys

from sacrerouge.commands import Subcommand
from sacrerouge.common import Params
from sacrerouge.data import EvalInstance, Metrics, MetricsDict
from sacrerouge.data.dataset_readers import DatasetReader
from sacrerouge.io import JsonlWriter
from sacrerouge.metrics import Metric
from sacrerouge.data.dataset_readers import *
from sacrerouge.metrics import *


def load_metrics(params: Params) -> List[Metric]:
    metrics = []
    for metric_params in params.pop('metrics'):
        metric = Metric.from_params(metric_params)
        metrics.append(metric)
    return metrics


def get_initial_micro_list(instances: List[EvalInstance]) -> List[Metrics]:
    micro_list = []
    for instance in instances:
        micro_list.append(Metrics(instance.instance_id, instance.summarizer_id, instance.summarizer_type))
    return micro_list


class EvaluateSubcommand(Subcommand):
    def __init__(self, cr, command_prefix):
        super().__init__()
        sub_prefix = command_prefix + ['evaluate']
        dataset_reader_command_args_lookup = dict()
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
                command_args.append({"name": "macro_output_jsonl"})
                command_args.append({"name": "micro_output_jsonl"})
                command_args.append({"name": "--silent", "action": "store_true"})
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
        summaries = [instance.summary for instance in instances]

        macro = MetricsDict()
        micro_list = get_initial_micro_list(instances)

        for metric in metrics:
            # Prepare the extra input arguments
            eval_args = []
            for field in metric.required_fields:
                eval_args.append([instance.fields[field] for instance in instances])

            # Score all the summaries
            this_macro, this_micro_list = metric.evaluate(summaries, *eval_args)

            # Update the global metrics dictionaries
            macro.update(this_macro)
            for micro, this_micro in zip(micro_list, this_micro_list):
                micro.metrics.update(this_micro)

        dirname = os.path.dirname(args.macro_output_json)
        if dirname:
            os.makedirs(dirname, exist_ok=True)

        serialized_macro = jsons.dumps({'metrics': macro}, jdkwargs={'indent': 2})
        with open(args.macro_output_json, 'w') as out:
            out.write(serialized_macro)
        if not args.silent:
            print(serialized_macro)

        with JsonlWriter(args.micro_output_jsonl) as out:
            for metrics_dict in micro_list:
                out.write(metrics_dict)
