import argparse
from overrides import overrides

from sacrerouge.commands import Subcommand
from sacrerouge.datasets import chaganty2018
from sacrerouge.datasets.duc_tac import duc2005, duc2006, duc2007, tac2008, tac2009, tac2010
from sacrerouge.datasets.multiling import multiling2011


class SetupDatasetSubcommand(Subcommand):
    def __init__(self, cr, command_prefix):
        super().__init__()
        sub_prefix = command_prefix + ["setup-dataset"]

        self.subcommands = [
            chaganty2018.Chaganty2018Subcommand(cr, sub_prefix),
            duc2005.DUC2005Subcommand(cr, sub_prefix),
            duc2006.DUC2006Subcommand(cr, sub_prefix),
            duc2007.DUC2007Subcommand(cr, sub_prefix),
            multiling2011.MultiLing2011Subcommand(cr, sub_prefix),
            tac2008.TAC2008Subcommand(cr, sub_prefix),
            tac2009.TAC2009Subcommand(cr, sub_prefix),
            tac2010.TAC2010Subcommand(cr, sub_prefix),
        ]