import argparse
from collections import defaultdict
from typing import Dict, List

from sacrerouge import build_argument_parser
from sacrerouge.data import Metrics, MetricsDict
from sacrerouge.data.types import ReferenceType, SummaryType
from sacrerouge.io import JsonlReader


def load_summaries(file_path: str) -> List[SummaryType]:
    fields = []
    for data in JsonlReader(file_path).read():
        fields.append(data['summary'])
    return fields


def load_references(file_path: str) -> List[ReferenceType]:
    fields = []
    for data in JsonlReader(file_path).read():
        if 'summary' in data:
            fields.append([data['summary']['text']])
        elif 'summaries' in data:
            fields.append([summary['text'] for summary in data['summaries']])
        elif 'reference' in data:
            fields.append([data['reference']['text']])
        elif 'references' in data:
            fields.append([reference['text'] for reference in data['references']])
    return fields


def load_metrics_dicts(file_path: str) -> Dict[str, Dict[str, MetricsDict]]:
    metrics_dicts = defaultdict(dict)
    with JsonlReader(file_path, Metrics) as f:
        for instance in f:
            metrics_dicts[instance.instance_id][instance.summarizer_id] = instance.metrics
    return metrics_dicts


def command_exists(parser: argparse.ArgumentParser, command: List[str]) -> bool:
    """
    Checks to see if a specific command exists in the `parser`. The `parser` should
    be the root `ArgumentParser` for the command. The method will traverse through
    the `parser` to see if the `command` exists. This method does not work for checking
    arguments of a specific command.
    """
    # _subparsers is none when no subcommands exist
    if parser._subparsers is None:
        return False

    for action in parser._subparsers._group_actions:
        for choice, subparser in action.choices.items():
            if choice == command[0]:
                if len(command) == 1:
                    # The whole command has been matched
                    return True
                else:
                    return command_exists(subparser, command[1:])

    # We didn't find the first command, so it doesn't exist
    return False


def sacrerouge_command_exists(command: List[str]) -> bool:
    """Verifies if the command exists for the 'sacrerouge' command."""
    parser = build_argument_parser()
    return command_exists(parser, command)