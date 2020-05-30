import argparse
from overrides import overrides

from sacrerouge.datasets.chaganty2018 import setup
from sacrerouge.commands import Subcommand
from sacrerouge.datasets.dataset_subcommand import DatasetSubcommand


class Chaganty2018Subcommand(DatasetSubcommand):
    def __init__(self, cr, command_prefix):
        args = []
        args.append({"name": "output_dir"})
        super().__init__(cr, command_prefix, "chaganty2018", args, self.run)

    @overrides
    def run(self, args):
        setup.setup(args.output_dir)
