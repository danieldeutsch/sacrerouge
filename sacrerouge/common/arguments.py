import argparse
import distutils.util
import inspect
import json
from typing import Type

from sacrerouge.common import Params, Registrable
from sacrerouge.common.from_params import _NO_DEFAULT, construct_arg
from sacrerouge.data.dataset_readers import DatasetReader
from sacrerouge.metrics import Metric


def get_dataset_reader_from_argument(argument: str) -> DatasetReader:
    if argument in Registrable._registry[DatasetReader]:
        type_, _ = Registrable._registry[DatasetReader][argument]
        return type_()
    else:
        params = Params(json.loads(argument))
        return DatasetReader.from_params(params)


def add_metric_arguments(parser: argparse.ArgumentParser, metric_type: Type):
    """Inspect the `metric`'s constructor and add an argument to the `parser` for each parameter."""
    signature = inspect.signature(metric_type.__init__)
    for param_name in signature.parameters:
        name = signature.parameters[param_name].name
        if name == 'self':
            continue  # Ignore self in constructor
        if name in ['args', 'kwargs']:
            continue  # args and kwargs are not supported
        default_value = signature.parameters[param_name].default
        annotation = signature.parameters[param_name].annotation

        kwargs = {}
        kwargs['required'] = default_value == signature.empty

        if annotation in [int, float, str]:
            kwargs['type'] = annotation
            if default_value != signature.empty:
                kwargs['default'] = default_value
        elif annotation is bool:
            kwargs['type'] = lambda arg: bool(distutils.util.strtobool(arg))
            if default_value != signature.empty:
                kwargs['default'] = default_value
        else:
            # There is either some type (but it's not a primitive (e.g. List[str])), or there's no typing information.
            # Either way, we assume the argument is a serialized json.
            kwargs['type'] = str
            if default_value is not None and default_value != signature.empty:
                kwargs['default'] = json.dumps(default_value)

        parser.add_argument(f'--{name}', **kwargs)


def get_metric_from_arguments(metric_type: Type, args: argparse.Namespace) -> Metric:
    kwargs = {}
    signature = inspect.signature(metric_type.__init__)
    for param_name in signature.parameters:
        name = signature.parameters[param_name].name
        if name == 'self':
            continue  # Ignore self in constructor
        if name in ['args', 'kwargs']:
            continue  # args and kwargs are not supported

        annotation = signature.parameters[param_name].annotation

        # If the type is a primitive, no extra work needs to be done
        argument = getattr(args, name)
        if annotation in [int, float, str, bool]:
            kwargs[name] = argument
        elif argument is None:
            # Just pass None
            kwargs[name] = None
        else:
            # Otherwise, we are going to try and parse it from a json as if it were parameter
            try:
                params = json.loads(argument)
                kwargs[name] = construct_arg(str(metric_type), name, params, annotation, _NO_DEFAULT)
            except (json.decoder.JSONDecodeError, TypeError):
                # Fall back to just passing the argument
                kwargs[name] = argument

    return metric_type(**kwargs)
