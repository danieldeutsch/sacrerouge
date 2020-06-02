import argparse
from overrides import overrides

from sacrerouge.commands import Subcommand
from sacrerouge.metrics import autosummeng, bewte, meteor, moverscore, simetrix, sumqe


@Subcommand.register('setup-metric')
class SetupMetricSubcommand(Subcommand):
    @overrides
    def add_subparser(self, parser: argparse._SubParsersAction):
        self.parser = parser.add_parser('setup-metric')
        subparsers = self.parser.add_subparsers()

        subcommands = [
            autosummeng.AutoSummENGSetupSubcommand(),
            bewte.BEwTESetupSubcommand(),
            meteor.MeteorSetupSubcommand(),
            moverscore.MoverScoreSetupSubcommand(),
            simetrix.SIMetrixSetupSubcommand(),
            sumqe.SumQESetupSubcommand(),
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
