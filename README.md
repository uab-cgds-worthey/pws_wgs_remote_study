# PWS - WGS Remote Study

<!-- markdown-link-check-disable -->
[![Linting-
Markdown,Shell](https://github.com/uab-cgds-worthey/pws_wgs_remote_study/actions/workflows/linting.yml/badge.svg)](https://github.com/uab-cgds-worthey/pws_wgs_remote_study/actions/workflows/linting.yml)
<!-- markdown-link-check-enable -->

A collection of scripts, figures, and plots used in analysis of phenotypes and genotypes from genome
sequences of 50 participants with Prader-Willi Syndrome. Analyses are broken down into specific
focuses described in more detail in the next section.

## Repository structure

* [viz_cnv_roh](viz_cnv_roh/README.md) - Visualize CNVs, ROH and coverage
* [pheno_mdx](pheno_mdx/README.md) - Analyze phenotypes and metadata, vizualize results, plot GS MDx Sankey diagram
* [survey_to_HPO](survey_to_HPO/README.md) - Build phenotype (HPO) profile for participants from their PWS survey

## Requirements

* For CNV and ROH visualization
  * Conda (v23+)
  * Snakemake (v6+)
* For Phenotype and MDx analysis
  * Conda (v23+)
* For HPO profile building
  * Conda (v23+)
* Common Requirements
  * Git v2.0+

## How to install

Installation starts with fetching the Git repo and cloning it:

```sh
git clone https://github.com/uab-cgds-worthey/pws_wgs_remote_study.git
cd pws_wgs_remote_study
```

## How to run

Refer to the specific [analysis subsection](#repository-structure) README for
instructions on running those specific parts of the analysis.

## Authors

* Manavalan Gajapathy
* Brandon M. Wilk
