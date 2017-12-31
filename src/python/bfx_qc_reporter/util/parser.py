#!/usr/bin/env python

import sys
import os
import argparse

def build_subparser(subparsers, source_file, description):
    name = os.path.basename(source_file[:-3]).replace("_", "-")
    help = next(filter(lambda line: len(line) > 0, description.split("\n")))
    return subparsers.add_parser(name=name, description=description, formatter_class=ArgParseFormatter, help=help)

def fail_parser(parser, msg):
    """ Prints the help message, then the error message, then exits. """
    parser.print_help()
    sys.stderr.write(msg + "\n")
    sys.exit(1)

class ArgParseFormatter(argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter):
    """
    A custom argparse formatter that adds in the default value for each opption,
    and does not line-wrap the help description and epilog.
    """
    pass
