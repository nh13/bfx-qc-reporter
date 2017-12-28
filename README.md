Bioinformatics QC Reporting Tools
====

Simple scripts to collate per-sample bioinformatic QC metrics.
Supports [fgbio](http://fulcrumgenomics.github.io/fgbio/), [Picard](http://broadinstitute.github.io/picard), and CSV metric files.

If you say to yourself, "all I want to do is see some QC metrics for my samples", you've come to the right place.

*** **This repository is under active development. Use at your own risk.** ***

## Reporting QC Metrics

The collation scripts are located in the `scripts` folder.

### Collating QC metrics

The `metrics2json.py` script will collate per-sample metric files into a single JSON file for consumption either by the user or by the `json2summaryreport.py` script. 
Additionally, a flattened CSV file will also be created.
All sample-specific metric files should live in a single directory, and that each metric file for each sample has the same metric extension. 
For example, the metric file for Picard's [`AlignmentSummaryMetrics`](http://broadinstitute.github.io/picard/picard-metric-definitions.html#AlignmentSummaryMetrics) could be located in `<output-dir>/<sample-name>.alignment_summary_metrics.txt`.
The file extension and metrics to be collated are user-configurable with the `--metric-defs` option; run `metrics2json.py --help` for more information.

#### Examples

Specifying the name of each sample individually:

```
python scripts/metrics2json.py \
    --output-dir <dir-with-metric-files> \
    --output-prefix <output-path-prefix> \
    --sample-names sample1 sample2 ... sampleN
```

Specifying the sample names using the output of [fgbio's](https://github.com/fulcrumgenomics/fgbio) [DemuxFastqs](fulcrumgenomics.github.io/fgbio/tools/latest/DemuxFastqs.html):

```
python scripts/metrics2json.py \
    --output-dir <dir-with-metric-files> \
    --output-prefix <output-path-prefix> \
    --demux-barcode-metrics <path/to/demux_barcode_metrics.txt>
```

### Creating a Summary Report

The `json2summaryreport.py` selects specific metrics from  the JSON output and reformats it into a comma-delimited file for downstream consumption.
Run `json2summaryreport.py --help` for more information.

#### Example

Using the default metrics to report:

```
    python /Users/nhomer/git/nh13/bfx-qc-reporter/scripts/json2summaryreport.py \
        --input </path/to/metrics.json> \
        --output </path/to/summary.csv>;
```

Specifying a custom set of metrics to report in `report_defs.csv`:

```
    python /Users/nhomer/git/nh13/bfx-qc-reporter/scripts/json2summaryreport.py \
        --input </path/to/metrics.json> \
        --report-defs report_defs.csv \
        --output </path/to/summary.csv>;
```

## Browsing Metrics in Webpage

The `web/index.html` webpage can be used to load the output of `metrics2json.py` to allow interactive browsing of metrics across one or more samples.
The page also allows the user to sub-select the metrics to display.

*** **This functionality is under active development.** ***

## Help Wanted

The scripts and webpage were written for my own needs, and quickly, on my own free time.
Please feel free to contribute!

## Example Metric JSON

```
{
     
    "Sample-1": {
        "Alignment Summary Metrics": {
            "FIRST_OF_PAIR": {
                "total_reads": 10000,
                "pf_reads": 10000,
                "pct_pf_reads": 1,
                "pf_noise_reads": 0,
                "pf_reads_aligned": 9999
            }
        },
        "Duplication Metrics": {
            "None": {
                "library": 1,
                "unpaired_reads_examined": 0,
                "read_pairs_examined": 10000,
                "secondary_or_supplementary_rds": 0,
                "unmapped_reads": 0,
                "unpaired_read_duplicates": 0,
                "read_pair_duplicates": 0,
                "read_pair_optical_duplicates": 0,
                "percent_duplication": 0,
                "estimated_library_size": ""
            }
        }
    },
    "Sample-2": {
        "Alignment Summary Metrics": {
            "FIRST_OF_PAIR": {
                "total_reads": 10000,
                "pf_reads": 10000,
                "pct_pf_reads": 1,
                "pf_noise_reads": 0,
                "pf_reads_aligned": 9999
            }
        },
        "Duplication Metrics": {
            "None": {
                "library": 1,
                "unpaired_reads_examined": 0,
                "read_pairs_examined": 10000,
                "secondary_or_supplementary_rds": 0,
                "unmapped_reads": 0,
                "unpaired_read_duplicates": 0,
                "read_pair_duplicates": 0,
                "read_pair_optical_duplicates": 0,
                "percent_duplication": 0,
                "estimated_library_size": ""
            }
        }
    }        
}
```

