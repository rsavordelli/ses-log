import argparse
from source.config import *
parser = argparse.ArgumentParser(prog="SESCLI")
parser.add_argument('--show-config', '-show', action='store_true',  help='Show current configuration')
parser.add_argument('--setup', action='store_true',  help='Setup CLI')
parser.add_argument('--delete-resources', '-set', action='store_true',  help='Delete all SES_LOG Resources created from the CLI')
args = parser.parse_args()


def get_args():
    if args.show_config:
        Config().show_config()
    if args.setup:
        Config().configure()
    if args.delete_resources:
        Config().delete_resources()
    if not any(vars(args).values()):
        parser.print_help()
