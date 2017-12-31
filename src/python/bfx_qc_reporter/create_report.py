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
    Creates a summary report from the output of the load-metrics command.

    # The Metrics to Report

    The --report-defs option specifies the path to the report definitions, 
    comma-delimited. Each line should contain four values: 
    1. The name of the metric group
    2. The category
    3. The metric name in the JSON
    3. The metric name to display in the report

    The first three values will be used to identify the metrics to report. 

    # Output Report

    The --output-prefix option specifies the path prefix for the output 
    files.  A JSON file will be written with just those metrics specified
    in the --report-defs file.  Additionally, a flattened CSV file will 
    also be created and have columns for:
    - the metric group name
    - the metric category
    - the metric name
    - for each sample, the value of the metric

    """

    parser = build_subparser(subparsers, source_file=__file__, description=description)

    parser.add_argument('--input', help='The path to the input file.', required=True)
    parser.add_argument('--output-prefix', help='The path prefix for the output files', required=True)
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

    def recursively_add(data, *args):
        """ Recursively adds a new dictionary at the given args. """
        for arg in args:
            if not arg in data:
                data[arg] = OrderedDict()
            data = data[arg]

    # Go through the report defs and print the relevant metrics
    sample_names = list(json_data.keys())
    header       = ["group", "category", "name"] + sample_names
    json_out     = OrderedDict([(name, OrderedDict()) for name in sample_names]) 
    csv_out      = [header]
    for report_def in report_defs:
        # get the metric to report
        group, category, name, display_name = report_def
        # get the values for the CSV output
        values = [sample_data[group][category][name] for sample_data in json_data.values()]
        values = [str(value) for value in values]
        values = [group, category, display_name] + values
        csv_out.append(values)
        # add the values for the JSON output
        for sample_name, sample_data in json_data.items():
            recursively_add(json_out[sample_name], group, category, name)
            json_out[sample_name][group][category][name] = sample_data[group][category][name] 

    # CSV output
    fn_csv = args.output_prefix + ".csv" 
    with open(fn_csv, "w") as fh:
        sys.stderr.write(f"Writing to {fh.name}\n")
        if args.transpose:
            num_columns = len(csv_out[0])
            for i in range(num_columns):
                values = [datum[i] for datum in csv_out]
                fh.write(",".join(values) + "\n")
        else:
            for datum in csv_out:
                fh.write(",".join(datum) + "\n")

    # JSON otput
    fn_json = args.output_prefix + ".json" 
    with open(fn_json, "w") as fh:
        sys.stderr.write(f"Writing to {fh.name}\n")
        fh.write(json.dumps(json_out, sort_keys=False, indent=4, separators=(',', ': ')))
