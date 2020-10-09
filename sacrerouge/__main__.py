import argparse

from sacrerouge.commands import correlate, evaluate, metric_command, score, setup_dataset, setup_metric, stat_sig_test


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    subcommands = [
        correlate.CorrelateSubcommand(),
        evaluate.EvaluateSubcommand(),
        score.ScoreSubcommand(),
        setup_dataset.SetupDatasetSubcommand(),
        setup_metric.SetupMetricSubcommand(),
        stat_sig_test.StatisticalSignificanceTestSubcommand(),
    ]
    for subcommand in subcommands:
        subcommand.add_subparser(subparsers)

    # Add a command for each individual metric
    metric_command.add_metric_subcommands(subparsers)

    args = parser.parse_args()
    if 'func' in dir(args):
        args.func(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
