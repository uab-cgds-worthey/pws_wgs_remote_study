# Visualize CNVs and ROHs



## Requirements

* Conda
* Snakemake

## How to run

```sh
# change into repo's root directory
cd /path/to/pws_wgs_remote_study/

# fetch and process gaps datasets
snakemake -s src/viz_cnv_roh/prep_dependencies.smk -p

# create and activate conda env
conda env create -f configs/viz_cnv_roh/envs/python_viz.yaml
conda activate python_viz_pws

# run viz script to visualize ROHs, CNVs and necessary annotations
# Note: Several data files are needed to run this script. See the script for more info. For each data file needed,
# we noted whether they are provided in this repo (full file or as an example) and how to create them.
python src/viz_cnv_roh/plot_roh_cnv.py
```

