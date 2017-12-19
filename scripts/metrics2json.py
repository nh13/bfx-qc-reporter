#!/usr/bin/env python

import os
import sys
import re
import argparse
from collections import OrderedDict
import json
from util.parser import *
from util.util import fail

def to_sample_names(path):
    """
    Infer the sample names and thus the sample file name prefix for all metrics
    from the metrics file produced by fgbio's DemuxFastqs.
    """
    sample_names = []
    with open(path, "r") as fh:
        line_iter = iter(line.rstrip("\r\n") for line in fh)
        header = [line.lower() for line in next(line_iter).split("\t")]
        for line in line_iter:
            sample_data  = line.split("\t")
            sample_dict  = OrderedDict(zip(header, sample_data))
            barcode_name = sample_dict["barcode_name"]
            library_name = sample_dict["library_name"]
            barcode      = sample_dict["barcode"]
            sample_name  = f"{barcode_name}-{library_name}-{barcode}"
            if barcode_name != "unmatched":
                sample_names.append(sample_name)
    return sample_names

def format_value(name, value):
    """
    Attempts to format the value as a float (if it has a "." in it) or an integer,
    otherwise returns the original value.
    """
    retval = value
    if "name" in name:
        pass
    elif "." in value:
        try:
            retval = float(value)
        except ValueError:
            pass
    else:
        try:
            retval = int(value)
        except ValueError:
            pass
    return retval

def to_dict_from_table(path, lines, category=None):
    """
    Converts a tabular (with header) file into a dictionary, with one
    key per metric category (or "None" if no category exists).  The value per category
    is a map from metric name to value.  All metric names will be changed to
    lowercase.
    """
    line_iter = iter(line for line in lines)
    row_dicts = []
    try:
        header = [line.lower() for line in next(line_iter).split("\t")]
    except StopIteration:
        sys.stderr.write(f"Warning: empty metric file: {path}\n")
        return OrderedDict()
    for line in line_iter:
        if not line:
            break
        row      = [value for value in line.split("\t")]
        row_dict = OrderedDict([(name, format_value(name, value)) for name, value in zip(header, row)])
        row_dicts.append(row_dict)

    data = OrderedDict()
    assert len(row_dicts) > 0
    if category:
        for row_dict in row_dicts:
            category_value = "-".join([str(row_dict[c]) for c in category])
            data[category_value] = row_dict
        return data
    else:
        assert len(row_dicts) == 1
        data = OrderedDict({"None" : row_dicts[0]})
    return data

def to_dict_from_picard(path, lines, category=None):
    """
    Converts in a Picard-style metric into a dictionary, with one key per
    metric category (or "None" if no category exists).  The value per category
    is a map from metric name to value.  All metric names will be changed to
    lowercase.
    """
    line_iter = iter(line for line in lines)
    for line in line_iter:
        if "## METRICS CLASS" in line:
            break
    return to_dict_from_table(path, line_iter, category)

def to_metric_dict(path, category=None):
    """
    Produces a dictionary of metrics and values, with one key per
    metric category (or "None" if no category exists).  The value per category
    is a map from metric name to value.  All metric names will be changed to
    lowercase.
    """
    with open(path, "r") as fh:
        lines = [line.rstrip("\r\n") for line in fh]
        if len(lines) == 0:
            sys.stderr.write(f"Warning: empty metric file: {path}\n")
            return OrderedDict()
        elif lines[0] == "## htsjdk.samtools.metrics.StringHeader":
            sys.stderr.write(f"Found Picard metric file: {path}\n")
            return to_dict_from_picard(path, lines, category)
        else:
            # assume just a table
            sys.stderr.write(f"Found tabular metric file: {path}\n")
            return to_dict_from_table(path, lines, category)

description="""
A tool to convert Picard and comma-separated per-sample metric files to JSON.

# Specifying Sample Names

The list of sample names will be used to find all metric files for a given 
sample as well as used to group all metrics from the same sample within the
output JSON.  There are three ways to specify the sample names:

1. The --sample-names option specifies each sample name individually.
2. The --demux-barcode-metrics option specifies a path to the metrics file 
   produced by fgbio's DemuxFastqs.  The sample name will be 
   "{barcode_name}-{library_name}-{barcode}".
3. If neither option is given, the first metric file extension will be used
   to find all sample metric files in the output directory. FIXME: implement?

# Definining the Metrics to Collate

The --metric-defs option gives the path to a comma-delimited file containing
four columns:

1. The unique name of the metric (ex. "Alignment Summary Metrics").
2. The file extension for the metric (ex. ".alignment_summary_metrics.txt")
3. Documentation for the metric (no commas) (ex. URL)
4. If the metric file has more than one row, a colon-delimited list of 
   column names that uniquely identifies each row, otherwise blank.

# Finding the Metric Files

The path to the file containing the metrics for specific sample is as follows:
    <output-dir>/<sample-name><file-extension>
This means the metric files for all samples should live in the same directory,
and metrics for a given sample should share the same path prefix.

# Output Files

The output JSON file will contain the following hierarchy:
    {
        "<sample-name>" : {
            "<metric-group-name>" : {
                "<metric-category>" : {
                    "<metric-name>" : <metric-value>,
                    "<metric-name>" : <metric-value>,
                    "<metric-name>" : <metric-value>,
                    ....

                },
                ...
            },
            ...
        },
        ...
    }
The <metric-group-name> is the name from the metric definition file. The
metric <metric-category> is either None if no category was given, or a 
dash-delimited list of the categries given.

The output CSV file contain the following columns:
- <metric-group-name>
- <metric-category>
- <metric-name>
- one column per sample with the metric value for that sample 
- file extension from the metric definition file
- documentation string from the metric definition file

# Metric Files Supported

## Picard Metrics

Metric files produced by Picard tools are supported.  If the metric has more
than one row, use the <metric-category> to uniquely identify the row, such
as "CATEGORY" for "AlignmentSummaryMetrics".

See: http://broadinstitute.github.io/picard/picard-metric-definitions.html

## Fbio Metrics

Metric files produced by fgbio are supported.

## CSV Files

Comma-delimited text files are supported, but must have the first row be the
names of the metrics (a header row).

"""

parser = argparse.ArgumentParser(formatter_class=ArgParseFormatter, description=description)
parser.add_argument('--output-dir', help='The path to the directory containing the metric files', required=True)
parser.add_argument('--output-prefix', help='The path prefix for the output files', required=True)
parser.add_argument('--metric-defs', help="The path to the metric definitions, comma-delimited.", required=False, 
        default=os.path.join(os.path.abspath(__file__), "resources", "metric_defs.csv"))
parser.add_argument('--sample-names', help="The sample name; a sample's metric file will be <output-dir>/<sample-name><file-extension>", required=False, action="append", default=[])
parser.add_argument('--demux-barcode-metrics', help="The path to the metrics file produced by fgbio's DemuxFastqs used to infer the sample prefixes.", required=False)
args = parser.parse_args()

if not os.path.isdir(args.output_dir):
    fail(f"--output was not a directory: '{args.output_dir}'")

# Read in the metric defintions to print
with open(args.metric_defs, "r") as fh:
    metrics_defs = OrderedDict()
    metrics_desc = OrderedDict()
    metrics_category = OrderedDict()
    for line_index, line in enumerate(fh):
        tokens = line.rstrip("\r\n").split(",")
        if len(tokens) != 4:
            line = line.rstrip("\r\n")
            fail(f"Expected four values on line #{line_index+1}, found {len(tokens)}: '{line}'")
        if tokens[0] in metrics_defs:
            fail(f"Metric '{tokens[0]}' already defined on line #{line_index+1}")
        metrics_defs[tokens[0]]     = tokens[1]
        metrics_desc[tokens[0]]     = tokens[2]
        metrics_category[tokens[0]] = tokens[3].lower().split(":") if tokens[3] else None

# Get the list of sample names
if args.demux_barcode_metrics and args.sample_names:
    fail_parser(parser, "Both --demux-barcode-metrics and --sample-prefix cannot be given.")
elif not args.demux_barcode_metrics and not args.sample_names:
    sample_names = []
    metric_ext = next(iter(metrics_defs.values()))
    for fn in os.listdir(args.output_dir):
        path = os.path.join(args.output_dir, fn)
        if os.path.isfile(path) and path.endswith(metric_ext):
            sample_names.append(fn[:len(fn)-len(metric_ext)])
    if not sample_names: fail_parser(parser, f"No samples were found in the output directory: {args.output_dir}")
elif args.demux_barcode_metrics:
    sample_names = to_sample_names(args.demux_barcode_metrics)
    if not sample_names: fail_parser(parser, f"No samples were found {args.demux_barcode_metrics}")
else:
    sample_names = args.sample_names
    if not sample_names: fail_parser(parser, "No samples were specified with --sample-prefix")

# Group the metrics by sample, metric group, category, and metric/value
metric_data = OrderedDict()
for sample_name in sample_names: # for each sample
    assert not sample_name in metric_data
    sample_dict = OrderedDict()
    for metric_name, metric_ext in metrics_defs.items(): # for each metric definition
        assert not metric_name in sample_dict
        path = os.path.join(args.output_dir, sample_name + metric_ext)
        if os.path.isfile(path):
            # get the metrics for the given sample and metric definition
            sample_dict[metric_name] = to_metric_dict(path, metrics_category[metric_name])
        else:
            sys.stderr.write(f"Warning: path does not exists for {metric_name}: {path}\n")
            sample_dict[metric_name] = OrderedDict()
    # store the metrics for this sample
    metric_data[sample_name] = sample_dict

# Write it to JSON
with open(args.output_prefix + ".json", "w") as fh:
    sys.stderr.write(f"Writing to {fh.name}\n")
    fh.write(json.dumps(metric_data, sort_keys=False, indent=4, separators=(',', ': ')))

# Write it to a flattened CSV
with open(args.output_prefix + ".csv", "w") as fh:
    sys.stderr.write(f"Writing to {fh.name}\n")

    header = ["Group", "Category", "Name"] + sample_names + ["File Extension,Documentation URL"]
    fh.write(",".join(header) + "\n")

    for metric_group_name, metric_group_data in metric_data[sample_names[0]].items():
        for category, metric_category_data in metric_group_data.items():
            for metric_name in metric_category_data.keys():
                def lookup(sample_data):
                    try:
                        return sample_data[metric_group_name][category][metric_name]
                    except KeyError:
                        return "Missing"
                metric_values = [lookup(sample_data) for sample_data in metric_data.values()]
                items = [metric_group_name, category, metric_name] + metric_values + [metrics_defs[metric_group_name]]
                items = [str(item) for item in items]
                items = items + [metrics_desc[metric_group_name]]
                fh.write(",".join(items) + "\n")
