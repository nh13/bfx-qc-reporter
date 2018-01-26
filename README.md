# Conda Recipe for bfx-qc-reporter

## Pre-requisites

This requires `conda-build` to be installed:

```
conda install -y -q conda-build
```

## Installation

To install locally and use your local channel:

```
conda-build .
conda install -y bfx-qc-reporter --use-local
conda config --add channels local
```
