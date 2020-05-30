from sacrerouge.commands import Subcommand

class DatasetSubcommand(Subcommand):
	def __init__(self, cr, command_prefix, command_name, args, func):
		super().__init__()
		cr.register_command(command_prefix + [command_name], args, func)