import argparse

class TreeNode(object):
	def __init__(self, title, args, children):
		self.title = title
		self.args = args
		self.children = children
		self.func = None
		self.defaults = None

	def __repr__(self):
		return "TreeNode[title = " + repr(self.title) + ", func = " + repr(self.func) + ", defaults = " + repr(self.defaults) + ", args = " + repr(self.args) + ", children = " + repr(self.children) + "]"

class CommandRegistry(object):
	def __init__(self, root_command):
		self.commands = dict()
		self.functions = dict()
		self.defaults = dict()
		self.root_command = root_command

	def register_command(self, path, args, func, defaults = None):
		self.commands[tuple(path)] = args
		self.functions[tuple(path)] = func
		self.defaults[tuple(path)] = defaults

	def build_command_tree(self):
		command_tree = TreeNode(self.root_command, [], [])
		for command_path_tuple, args in self.commands.items():
			func = self.functions[command_path_tuple]
			defaults = self.defaults[command_path_tuple]
			command_path = list(command_path_tuple)
			node = command_tree
			for command_keyword in command_path:
				next_node = None
				for child in node.children:
					if child.title == command_keyword:
						next_node = child
				if next_node == None:
					next_node = TreeNode(command_keyword, [], [])
					node.children.append(next_node)
				node = next_node
				if command_keyword == command_path[-1]:
					node.args = args
					node.func = func
					node.defaults = defaults
		return command_tree

	def add_command_to_parser(self, node, parser):
		if not node.children == []:
			# subcommands
			subparser = parser.add_subparsers()
			for sub_command in node.children:
				parser_inner = subparser.add_parser(sub_command.title)
				self.add_command_to_parser(sub_command, parser_inner)
		else:
			default_values = node.defaults if node.defaults is not None else dict()
			default_values["func"] = node.func
			parser.set_defaults(**default_values) # Dictionary expansion
			for arg in node.args:
				#parser.add_argument(arg)
				if 'nargs' in arg:
					parser.add_argument(arg['name'], nargs=arg['nargs'])
				elif 'choices' in arg:
					parser.add_argument(arg['name'], choices=arg['choices'])
				elif 'action' in arg:
					parser.add_argument(arg['name'], action=arg['action'])
				elif 'default' in arg:
					parser.add_argument(arg['name'], nargs='?', const=arg['default'])
				else:
					parser.add_argument(arg['name'])

	def create_parser(self):
		command_tree = self.build_command_tree()
		#print(repr(command_tree))
		parser = argparse.ArgumentParser()
		self.add_command_to_parser(command_tree, parser)
		return parser