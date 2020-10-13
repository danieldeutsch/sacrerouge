import argparse

from sacrerouge.common import Registrable
from sacrerouge.common.util import import_module_and_submodules
from sacrerouge.commands import RootSubcommand, metric_command


def build_argument_parser():
    # Ensure all of the subcommands have been loaded
    import_module_and_submodules('sacrerouge')

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    # Add all of the root-level commands using the registry
    for name, (cls_, _) in sorted(Registrable._registry[RootSubcommand].items()):
        cls_().add_subparser(subparsers)

    # Add a command for each individual metric
    metric_command.add_metric_subcommands(subparsers)
    return parser