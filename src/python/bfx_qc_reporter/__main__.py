import sys
import argparse
from bfx_qc_reporter.util.parser import *
from bfx_qc_reporter import create_report
from bfx_qc_reporter import load_metrics

def main(args=None):
    """The main routine."""
    
    parser = argparse.ArgumentParser(prog="bfx-qc-reporter")

    subparsers = parser.add_subparsers(dest="subcommand")
    subparsers.required = True
    
    # Add subparsers here
    create_report.add_subparser(subparsers=subparsers)
    load_metrics.add_subparser(subparsers=subparsers)

    args = parser.parse_args(args=args)
    args.func(parser, args)


if __name__ == "__main__":
    main()
