import argparse
from overrides import overrides

from sacrerouge.commands import Subcommand
from sacrerouge.metrics import autosummeng, bertscore, bewte, meteor, moverscore, pyreval, python_rouge, rouge, simetrix, sumqe


class SetupMetricSubcommand(Subcommand):
    @overrides
    def add_subparser(self, parser: argparse._SubParsersAction):
        description = 'Setup an evaluation metric'
        self.parser = parser.add_parser('setup-metric', description=description, help=description)
        subparsers = self.parser.add_subparsers()

        subcommands = [
            autosummeng.AutoSummENGSetupSubcommand(),
            bertscore.BertScoreSetupSubcommand(),
            bewte.BEwTESetupSubcommand(),
            meteor.MeteorSetupSubcommand(),
            moverscore.MoverScoreSetupSubcommand(),
            pyreval.PyrEvalSetupSubcommand(),
            python_rouge.PythonRougeSetupSubcommand(),
            rouge.RougeSetupSubcommand(),
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
