import sys
import argparse
from .util.parser import *
from . import json2summaryreport
from . import metrics2json

def main(args=None):
    """The main routine."""
    
    parser = argparse.ArgumentParser(prog="bfx-qc-reporter")

    subparsers = parser.add_subparsers(dest="subcommand")
    subparsers.required = True
    
    # Add subparsers here
    json2summaryreport.add_subparser(subparsers=subparsers)
    metrics2json.add_subparser(subparsers=subparsers)

    args = parser.parse_args(args=args)
    args.func(args)


if __name__ == "__main__":
    main()
