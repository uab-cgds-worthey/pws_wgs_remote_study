# Visualize CNVs and ROHs



## Requirements

* Conda
* Snakemake

## How to run

### Fetch and process gaps datasets

```sh
# change into repo's root directory
cd /path/to/pws_wgs_remote_study/

# fetch and process gaps datasets
snakemake -s src/viz_cnv_roh/prep_dependencies.smk -p
```

### Visualize ROHs and CNVs

```sh
# change into repo's root directory
cd /path/to/pws_wgs_remote_study/

# create and activate conda env
conda env create -f configs/viz_cnv_roh/envs/python_viz.yaml
conda activate python_viz_pws

# run viz script to visualize ROHs, CNVs and necessary annotations
# Note: Several data files are needed to run this script. See the script for more info. For each data file needed,
# we noted whether they are provided in this repo (full file or as an example) and how to create them.
python src/viz_cnv_roh/plot_roh_cnv.py
```

### Visualize ROHs, CNVs and coverage

* Calculate coverage using mosdepth

```sh
# change into repo's root directory
cd /path/to/pws_wgs_remote_study/

# create and activate conda env
conda env create -f configs/viz_cnv_roh/envs/mosdepth.yaml
conda activate mosdepth_cov

# now run mosdepth
REGION_SIZE="500"
CHROM="chr15"
REF="/data/project/worthey_lab/datasets_central/human_reference_genome/processed/GRCh38/no_alt_rel20190408/GCA_000001405.15_GRCh38_no_alt_analysis_set.fna"

for SAMPLE in A B C
do
    echo "Working on $SAMPLE"
    IN_CRAM="path/to/${SAMPLE}.cram"
    OUTDIR="data/processed/mosdepth/${CHROM}/${SAMPLE}"
    mkdir -p $OUTDIR
    OUT_PREFIX="${OUTDIR}/${SAMPLE}"

    mosdepth \
        --fast-mode \
        --no-per-base  \
        --by $REGION_SIZE \
        --chrom $CHROM \
        --fasta $REF \
        $OUT_PREFIX \
        $IN_CRAM
done
```

* Now visualize ROH, CNVs and coverage

```sh
# change into repo's root directory
cd /path/to/pws_wgs_remote_study/

# create, if not already, and activate conda env
conda env create -f configs/viz_cnv_roh/envs/python_viz.yaml
conda activate python_viz_pws

# run viz script to visualize ROHs, CNVs, coverage and necessary annotations.
# Note: Several data files are needed to run this script. See the script for more info. For each data file needed,
# we noted whether they are provided in this repo (full file or as an example) and how to create them.
python src/viz_cnv_roh/plot_roh_cnv_cov.py
```
