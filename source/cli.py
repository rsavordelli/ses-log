import argparse
from source.config import *
parser = argparse.ArgumentParser(prog="SESCLI")
parser.add_argument('--show-config', '-s', action='store_true',  help='show current configuration')
parser.add_argument('--configure','-cfg', action='store_true',  help='setup CLI and resources')
parser.add_argument('--delete-resources', '-dr', action='store_true',  help='delete all Resources created from the CLI')
args = parser.parse_args()


def get_args():
    if args.show_config:
        Config().show_config()
    if args.configure:
        Config().configure()
    if args.delete_resources:
        Config().delete_resources()
    if not any(vars(args).values()):
        parser.print_help()
