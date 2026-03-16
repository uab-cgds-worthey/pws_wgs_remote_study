"""
Preps necessary gap regions from external datasets

# command to use.
snakemake -s src/viz_cnv_roh/prep_dependencies.smk -p
"""

WORKFLOW_PATH = Path(workflow.basedir).parents[2]

EXTERNAL_DIR = Path("data/external")
PROCESSED_DIR = Path("data/processed")

GENOME_BUILD_LIST = ["hg38"]


############   CONSTRAINTS   ############
wildcard_constraints:
    genome_build="|".join(GENOME_BUILD_LIST),


rule all:
    input:
        expand(str(EXTERNAL_DIR / "gaps" / "gaps_{genome_build}.txt.gz"), genome_build=GENOME_BUILD_LIST),
        expand(str(EXTERNAL_DIR / "cytoband" / "cytoBand_{genome_build}.txt.gz"), genome_build=GENOME_BUILD_LIST),
        expand(str(PROCESSED_DIR / "gaps" / "aggregated_gaps_{genome_build}.bed"), genome_build=GENOME_BUILD_LIST),


rule download_gaps:
    output:
        EXTERNAL_DIR / "gaps" / "gaps_{genome_build}.txt.gz",
    message:
        "Download UCSC gaps for {wildcards.genome_build}"
    params:
        url="https://hgdownload.cse.ucsc.edu/goldenPath/{genome_build}/database/gap.txt.gz",
    shell:
        r"""
        curl -L -o {output} {params.url}
        """


rule download_cytoband:
    output:
        EXTERNAL_DIR / "cytoband" / "cytoBand_{genome_build}.txt.gz",
    message:
        "Download UCSC cytoband for {wildcards.genome_build}"
    params:
        url="https://hgdownload.cse.ucsc.edu/goldenPath/{genome_build}/database/cytoBand.txt.gz",
    shell:
        r"""
        curl -L -o {output} {params.url}
        """


rule prep_gaps_data:
    input:
        gap=EXTERNAL_DIR / "gaps" / "gaps_{genome_build}.txt.gz",
        cytoband=EXTERNAL_DIR / "cytoband" / "cytoBand_{genome_build}.txt.gz",
    output:
        tmpfile=temp(PROCESSED_DIR / "gaps" / "aggregated_gaps_{genome_build}_tmp.tsv"),
        final=PROCESSED_DIR / "gaps" / "aggregated_gaps_{genome_build}.bed",
    message:
        "Aggregate  gap regions of interest. Centromere info is available as part of hg19 gaps but not for hg38."
        "So centromere info was obtained from cytoband file."
    shell:
        r"""
        # extract regions of interest from gaps file
        zcat {input.gap} \
            | awk '$2 !~ /_/' \
            | grep -e heterochromatin -e "short_arm" -e telomere \
            | cut -f 2,3,4,8 \
            > {output.tmpfile}

        # extract regions of interest from cytoband file
        zcat {input.cytoband} \
            | grep "acen" \
            | cut -f 1-3,5 \
            >> {output.tmpfile}

        # sort it
        sort -k1,1 -k2,2n -k3,3n {output.tmpfile} > {output.final}
        """
