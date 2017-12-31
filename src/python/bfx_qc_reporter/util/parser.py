#!/usr/bin/env python

import sys
import argparse

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
