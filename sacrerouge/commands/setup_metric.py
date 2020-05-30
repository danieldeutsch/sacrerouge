import argparse
from overrides import overrides

from sacrerouge.commands import Subcommand
from sacrerouge.metrics import autosummeng, bewte, meteor, moverscore, simetrix, sumqe


class SetupMetricSubcommand(Subcommand):
    def __init__(self, cr, command_prefix):
        super().__init__()
        sub_prefix = command_prefix + ["setup-metric"]

        self.subcommands = [
            autosummeng.AutoSummENGSetupSubcommand(cr, sub_prefix),
            bewte.BEwTESetupSubcommand(cr, sub_prefix),
            meteor.MeteorSetupSubcommand(cr, sub_prefix),
            moverscore.MoverScoreSetupSubcommand(cr, sub_prefix),
            simetrix.SIMetrixSetupSubcommand(cr, sub_prefix),
            sumqe.SumQESetupSubcommand(cr, sub_prefix),
        ]