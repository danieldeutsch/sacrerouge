import argparse
from overrides import overrides

from sacrerouge.datasets.duc_tac.duc2006 import metrics, pyramids, task1
from sacrerouge.commands import Subcommand
from sacrerouge.datasets.dataset_subcommand import DatasetSubcommand


class DUC2006Subcommand(DatasetSubcommand):
    def __init__(self, cr, command_prefix):
        args = []
        args.append({"name": "data_root"})
        args.append({"name": "output_dir"})
        super().__init__(cr, command_prefix, "duc2006", args, self.run)

    @overrides
    def run(self, args):
        task1.setup(args.data_root, args.output_dir)
        metrics.setup(args.data_root, args.output_dir)
        pyramids.setup(args.data_root, args.output_dir)
