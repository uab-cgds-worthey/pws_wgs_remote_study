# Phenotype analysis and GS diagnosis plotting for PWS WGS Cohort

<!-- markdown-link-check-disable -->
[![Perform linting -
Markdown](https://github.com/uab-cgds-worthey/PWS-Reporting/actions/workflows/linting.yml/badge.svg)](https://github.com/uab-cgds-worthey/PWS-Reporting/actions/workflows/linting.yml)
<!-- markdown-link-check-enable -->

Phenotypic comparison of groups of participants in the PWS WGS Cohort based on molecular diagnosis for PWS.
Sankey diagram for plotting the PWS molecular cause as determined by GS compared from the reported
molecular cause.

## Requirements

- Anaconda3 or Mamba
- Git v2.0+

## How to install

Installation starts with building the conda environment for running the 2 notebooks used for the analysis.
It can built from this subsection of the repo directory like

```sh
cd pheno_mdx
# build environment using conda
conda env create -f env/conda-env.yml
```

the environemnt can be activated via

```sh
conda activate pws-pheno
```

## How to run

Make sure the conda environment is activated (see above) and start the Jupyter server

```sh
jupyter lab
```

In the Jupyter lab interface that opens in a web browser, navigate into the `notebooks`
directory, double click the notebook you'd like to run, and click the run button for the
notebook in the tab that opens.

Metadata and phenotypes from participants are protected data and would need to be obtained
from the corresponding authors. An example of how the data was formatted is included in
the [example input CSV file](data/raw/pws-reported-primary-findings-variants.csv).
All output data and figures can be found in the [processed data directory](data/processed).
