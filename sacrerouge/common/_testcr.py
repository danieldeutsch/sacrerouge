from command_registry import *
import argparse

def test_status(args):
	print("test_status")
	print(args)
def test_remote_add(args):
	print("test_remote_add")
	print(args)
def test_remote_remove(args):
	print("test_remote_remove")
	print(args)

def main():
	cr = CommandRegistry("testgit")
	cr.register_command(["status"], [], test_status)
	cr.register_command(["remote", "add"], ["name"], test_remote_add)
	cr.register_command(["remote", "remove"], ["name"], test_remote_remove)
	parser = cr.create_parser()
	arguments = vars(parser.parse_args())
	func = arguments['func']
	arguments.pop('func')
	func(arguments)

main()