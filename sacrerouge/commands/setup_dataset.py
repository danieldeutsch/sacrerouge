import argparse
from overrides import overrides

from sacrerouge.commands import Subcommand
from sacrerouge.datasets import chaganty2018
from sacrerouge.datasets.duc_tac import duc2001, duc2002, duc2003, duc2004, duc2005, duc2006, duc2007, tac2008, tac2009, tac2010, tac2011
from sacrerouge.datasets.multiling import multiling2011


class SetupDatasetSubcommand(Subcommand):
    @overrides
    def add_subparser(self, parser: argparse._SubParsersAction):
        self.parser = parser.add_parser('setup-dataset')
        subparsers = self.parser.add_subparsers()

        subcommands = [
            chaganty2018.Chaganty2018Subcommand(),
            duc2001.DUC2001Subcommand(),
            duc2002.DUC2002Subcommand(),
            duc2003.DUC2003Subcommand(),
            duc2004.DUC2004Subcommand(),
            duc2005.DUC2005Subcommand(),
            duc2006.DUC2006Subcommand(),
            duc2007.DUC2007Subcommand(),
            multiling2011.MultiLing2011Subcommand(),
            tac2008.TAC2008Subcommand(),
            tac2009.TAC2009Subcommand(),
            tac2010.TAC2010Subcommand(),
            tac2011.TAC2011Subcommand(),
        ]
        for subcommand in subcommands:
            subcommand.add_subparser(subparsers)

        self.parser.set_defaults(func=self.run)

    @overrides
    def run(self, args):
        if 'subfunc' in dir(args):
            args.subfunc(args)
        else:
            self.parser.print_help()
