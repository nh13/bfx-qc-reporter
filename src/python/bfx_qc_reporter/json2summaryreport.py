#!/usr/bin/env python

import os
import sys
import re
import argparse
from collections import OrderedDict
import json
from .util.parser import *

def add_subparser(subparsers):
    description="""
    A tool to produce a summary report from a JSON produced by metrics2json.py.

    # The Metrics to Report

    The --report-defs option specifies the path to the report definitions, 
    comma-delimited. Each line should contain four values: 
    1. The name of the metric group
    2. The category
    3. The metric name in the JSON
    3. The metric name to display in the report

    The first three values will be used to identify the metrics to report. 

    # Output Report

    The --output option species the path to the output file, by default 
    writing to standard output.  The output will be comma-delmited, and
    have columns for:
    - the metric group name
    - the metric category
    - the metric name
    - for each sample, the value of the metric

    """
    parser = subparsers.add_parser(name=os.path.basename(__file__[:-3]), description=description, formatter_class=ArgParseFormatter)

    parser.add_argument('--input', help='The path to the input file.', required=True)
    parser.add_argument('--output', help='The path to the output file.', required=False)
    parser.add_argument('--transpose', help='Transpose the rows and columns.', required=False, action='store_true', default=False)
    parser.add_argument('--report-defs', help="The path to the report definitions.", required=False, default=os.path.join(os.path.abspath(__file__), "resources", "report_defs.csv"))
    parser.set_defaults(func=main)

    return parser

def main(args):

    # Read in the JSON data
    with open(args.input, "r") as fh:
        json_string = ""
        for line in fh:
            json_string += line
        json_data = json.loads(json_string, object_pairs_hook=OrderedDict)

    # Read in the report definitions
    with open(args.report_defs, "r") as fh:
        report_defs = []
        for line in fh:
            if line.startswith("#"):
                continue
            report_defs.append(line.rstrip("\r\n").split(","))

    # Go through the report defs and print the relevant metrics
    sample_names = list(json_data.keys())
    header = ["group", "category", "name"] + sample_names
    data = []
    data.append(header)
    for report_def in report_defs:
        group, category, name, display_name = report_def
        values = [sample_data[group][category][name] for sample_data in json_data.values()]
        values = [str(value) for value in values]
        values = [group, category, display_name] + values
        data.append(values)

    if args.output:
        fh = open(args.output, "w")
    else:
        fh = sys.stdout

    if args.transpose:
        num_columns = len(data[0])
        for i in range(num_columns):
            values = [datum[i] for datum in data]
            fh.write(",".join(values) + "\n")
    else:
        for datum in data:
            fh.write(",".join(datum) + "\n")

    fh.write(",".join(values) + "\n")
    fh.close()

