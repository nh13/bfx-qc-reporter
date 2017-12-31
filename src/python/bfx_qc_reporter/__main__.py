import sys
import argparse
from .util.parser import *
from . import create_report
from . import load_metrics

def main(args=None):
    """The main routine."""
    
    parser = argparse.ArgumentParser(prog="bfx-qc-reporter")

    subparsers = parser.add_subparsers(dest="subcommand")
    subparsers.required = True
    
    # Add subparsers here
    create_report.add_subparser(subparsers=subparsers)
    load_metrics.add_subparser(subparsers=subparsers)

    args = parser.parse_args(args=args)
    args.func(args)


if __name__ == "__main__":
    main()
