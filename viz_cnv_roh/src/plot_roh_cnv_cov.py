"""
Visualizes CNV, ROH and coverage data along with useful annotations.
This script was modified from src/plot_roh_cnv.py to add viz support for coverage data.
See if __name__ == "__main__" section for data files needed.
"""

from pathlib import Path
from string import Template
from time import strftime

import matplotlib.patches as patches
import matplotlib.pyplot as plt
import pandas as pd
import pyranges as pr
import yaml
from adjustText import adjust_text
from matplotlib.lines import Line2D


def get_samplelist(fpath, diagnosis_group):
    "read sample configfile"

    with open(fpath) as fh:
        data = yaml.safe_load(fh)

    if isinstance(data[diagnosis_group], list):
        samples = data[diagnosis_group]
    elif isinstance(data[diagnosis_group], dict):
        samples = []
        for value in data[diagnosis_group].values():
            samples += value

    return samples


def get_samplename_map(fpath):
    "read sample name mapping"

    df = pd.read_csv(fpath, sep="\t")

    name_dict = df.set_index("CGDS ID")["Participant Paper ID(new)"].to_dict()

    return name_dict


def slice_data_by_region(df, query_region):
    "restrict data to region of interest"

    pr_data = pr.PyRanges(df)

    chromosome = query_region[0]
    if len(query_region) == 1:
        sliced_df = pr_data[chromosome].df
    else:
        sliced_df = pr_data[chromosome, query_region[1] : query_region[2]].df
        sliced_df = sliced_df.reset_index(drop=True)

        # modify pyranges start and end positions to match query region postions
        if len(sliced_df):
            if query_region[1] > sliced_df.loc[0, "Start"]:
                sliced_df.loc[0, "Start"] = query_region[1]

            if query_region[2] < sliced_df.loc[len(sliced_df) - 1, "End"]:
                sliced_df.loc[len(sliced_df) - 1, "End"] = query_region[2]

    return sliced_df


def define_colors():
    "define color configs for various types of data"

    colors = {}

    colors["cytoband"] = {
        "gneg": "white",
        "gpos25": "#D9D9D9",
        "gpos50": "#979797",
        "gpos75": "#636363",
        "gpos100": "black",
        "gvar": "#A0A0F2",
        "stalk": "#C0C0C0",
        "acen": "red",
    }

    colors["genes"] = {
        "biallelic": "gray",
        "paternal": "blue",
        "maternal": "brown",
        "bp_genes_of_interest": "black",
    }

    colors["roh"] = {
        "pass": "#1b9e77",
        # "low_confidence": "#3ddeae",
    }

    colors["fp_roh_gaps"] = {
        "fp_gaps": "#3ddeae",
    }

    colors["cnv"] = {
        "DEL": "#7570b3",
        "DUP": "#d95f02",
    }

    colors["breakpoint"] = "yellow"

    return colors


def read_gaps_data(f):
    df = pd.read_csv(f, sep="\t", names=["Chromosome", "Start", "End", "Name"])

    pr_data = pr.PyRanges(df)

    return pr_data


def get_ignore_cnv_data(f):
    df = pd.read_csv(f, sep="\t")

    data = {}
    for sample in df["sample"].unique():
        data[sample] = pr.PyRanges(df.loc[df["sample"] == sample, :])

    return data


def read_cytoband_data(f, query_region):
    "read cytoband data and return rows overlapping the query region"

    columns = ["Chromosome", "Start", "End", "Name", "stain"]
    df = pd.read_csv(f, sep="\t", names=columns)

    sliced_df = slice_data_by_region(df, query_region)

    return sliced_df


def plot_patches(ax, df, source, colors, ylabel, annotation=False):
    "plot data as rectangle patches"

    # Define y-coordinates for the bands
    height = 2 if source in ["cnv", "roh", "fp_roh_gaps"] else 1

    x_list = []
    y_list = []
    name_list = []
    for _, row in df.iterrows():
        start = row["Start"]
        end = row["End"]

        linewidth = 0
        if source == "cytoband":
            stain = row["stain"]
            color = colors[stain]
            edgecolor = "black"
            name = row["Name"]
            linewidth = 0.2
        elif source == "genes":
            color = colors[row["expression"]]
            edgecolor = color
            name = row["Name"]
            linewidth = 0.2
        elif source == "breakpoint":
            color = colors
            edgecolor = "black"
            name = row["Name"]
            linewidth = 0.2
        elif source == "roh":
            color = colors[row["filter_pass"]]
            edgecolor = color
        elif source == "fp_roh_gaps":
            color = colors["fp_gaps"]
            edgecolor = color
        elif source == "cnv":
            color = colors[row["cnv_type"]]
            edgecolor = color

        # Draw the rectangle blocks
        ax.add_patch(
            patches.Rectangle(
                (start, 0),
                end - start,
                height,
                edgecolor=edgecolor,
                linewidth=linewidth,
                facecolor=color,
            )
        )

        # controls annotation of small nucleolar RNA names
        if source == "genes" and name.startswith("SNORD"):
            if name == "SNORD116-15":
                name = "SNORD116"
            elif name == "SNORD115-25":
                name = "SNORD115"
            else:
                continue
        # else:
        #     print(name)

        # Add annotation
        if annotation:
            x_list.append((start + end) / 2)
            y_list.append(2)
            name_list.append(name)

    # Set yaxis limits; needs to be defined before adjust_text usage
    if source in ["genes"]:
        ax.set_ylim(0, 6.5)
    elif source in ["cytoband", "breakpoint"]:
        ax.set_ylim(0, 3.5)
    else:
        ax.set_ylim(0, height)

    # modelled after the script here - https://github.com/Phlya/adjustText/issues/182#issuecomment-2275589388
    # adjust text labels
    if annotation and len(x_list):
        annotation_text = []
        for name, x, y in zip(name_list, x_list, y_list):
            annotation_color = "red" if name.startswith("GOLG") else "black"
            annotation_text.append(
                ax.text(
                    x,
                    y,
                    name,
                    rotation=90,  # any other angle did not work well with adjust_text
                    fontdict={"fontsize": 8},
                    color=annotation_color,
                )
            )

        ax.plot(x_list, y_list, c="white")  # hidden plotting necessary to get adjust_text working

        # now adjust the text position so that they are not crowded
        adjtexts, _ = adjust_text(
            annotation_text,
            avoid_self=False,
            only_move="x",  # Only allow movement vertically
            max_move=None,
            ensure_inside_axes=True,
            force_pull=(0, 0),
            ax=ax,
            force_text=(0.05, 0),
        )

        # now add connector lines
        ii = -1
        for text in adjtexts:
            ii = ii + 1
            x_adjusted, _ = text.get_position()
            line = Line2D(
                [x_list[ii], x_list[ii], x_adjusted, x_adjusted],
                [1, 1.2, 1.5, 1.8],
                clip_on=False,
                # color=cm_pastel2[ii],
                linewidth=0.75,
            )
            ax.add_line(line)

    if source in ["cytoband", "breakpoint", "genes"]:
        # hide ticks and labels
        ax.set_yticklabels([])
        ax.set_yticks([])
    else:
        ax.yaxis.set_label_position("right")
        ax.yaxis.tick_right()

    # no plot borders
    # ax.axis("off")

    # color the spines, ticks and labels
    for spine in ax.spines.values():
        spine.set_edgecolor("darkgrey")
    ax.tick_params(colors="darkgrey", which="both")
    ylabel_pos = 0.5 if source in ["cytoband", "breakpoint", "genes"] else 0.5
    ax.yaxis.set_label_position("left")
    ax.set_ylabel(ylabel, rotation=0, y=ylabel_pos, ha="right")

    return None


def read_breakpoint_data(f, query_region):
    df = pd.read_csv(f, sep="\t", names=["Chromosome", "Start", "End", "Name"])

    # restrict to region of interest
    sliced_df = slice_data_by_region(df, query_region)

    return sliced_df


def read_genes_data(f, query_region):
    df = pd.read_csv(f, sep="\t")
    df = df.rename(
        columns={
            "#chrom": "Chromosome",
            "chromStart": "Start",
            "chromEnd": "End",
            "symbol": "Name",
        }
    )

    # restrict to region of interest
    sliced_df = slice_data_by_region(df, query_region)

    if len(sliced_df):
        # remove duplicate rows
        sliced_df.drop_duplicates(inplace=True, ignore_index=True)

        # retain only the landmark genes
        sliced_df.dropna(subset=["expression"], inplace=True, ignore_index=True)

        # Exclude rows with expression col value "bp_genes_of_interest" for full chromosome view
        if len(query_region) == 1:
            sliced_df = sliced_df.loc[~(sliced_df["expression"] == "bp_genes_of_interest"), :]

    return sliced_df


def read_roh_data(fpath, query_region, min_roh_mb=None):
    df = pd.read_csv(fpath, sep="\t")
    df = df.rename(columns={"#Chromosome": "Chromosome"})

    # retain rows of interest
    # filters_of_interest = ["pass", "low_confidence"]
    filters_of_interest = ["pass"]
    filter_df = df.loc[df["filter_pass"].isin(filters_of_interest), :]

    # filter by size
    if min_roh_mb:
        filter_df = filter_df.loc[filter_df["size_mb"] >= min_roh_mb, :]

    # restrict to region of interest
    sliced_df = slice_data_by_region(filter_df, query_region)

    return sliced_df


def read_falsePos_roh_gaps(fpath, query_region, sample):
    df = pd.read_csv(fpath, sep="\t")

    sample_df = df.loc[df["Sample"] == sample, :]

    # restrict to region of interest
    sliced_df = slice_data_by_region(sample_df, query_region)

    return sliced_df


def read_cnv_data(fpath, gaps_pr, cnv_ignore_pr, query_region, overlap_threshold=0.25):
    """
    read cnv data, remove calls overlapping gaps and calls that user wants to ignore
    and then return calls present in query region
    """

    df = pd.read_csv(fpath, sep="\t")
    df = df.rename(
        columns={
            "#chromosome": "Chromosome",
            "start": "Start",
            "end": "End",
        }
    )

    # remove explicit calls that user wants to ignore
    ignore_overlap_df = pr.PyRanges(df).coverage(cnv_ignore_pr).df
    filt_df = df.loc[ignore_overlap_df["FractionOverlaps"] < 1, :].reset_index(drop=True)

    if len(filt_df) != (len(df) - len(cnv_ignore_pr)):
        print("No. of calls remaining after ignored CNVs does not match expectations")
        print(f"CNV file: {fpath}")
        print(f"No. of CNVs to be ignored: {len(cnv_ignore_pr)}")
        print(f"No. of CNVs before and after filtering them: {len(df), len(filt_df)}")
        raise SystemExit(1)

    # remove calls overlapping gaps based on input threshold
    gaps_overlap_df = pr.PyRanges(filt_df).coverage(gaps_pr).df
    gaps_removed_df = filt_df.loc[
        gaps_overlap_df["FractionOverlaps"] < overlap_threshold, :
    ].reset_index(drop=True)

    # restrict to region of interest
    sliced_df = slice_data_by_region(gaps_removed_df, query_region)

    return sliced_df


def read_coverage_data(fpath, query_region):
    """
    Reads mosdepth coverage depth and normalizes depth
    """

    df = pd.read_csv(fpath, sep="\t", header=None, names=["Chromosome", "Start", "End", "Depth"])

    # restrict to chromosome in query
    df = df.loc[df["Chromosome"] == query_region[0], :]

    # calc midpoint for plotting purposes admd
    df["midpoint"] = (df["Start"] + df["End"]) / 2

    # normalize depth
    df["depth_normalized"] = df["Depth"] / df["Depth"].median()

    return df


def plot_coverage(ax, df):
    """
    plots coverage as a line plot
    """

    ax.axhline(y=1, linestyle="--", linewidth=0.8, color="red")
    ax.plot(df["midpoint"], df["depth_normalized"], color="black", linewidth=0.025)

    return None


def main(
    sample_config_f,
    samplename_map_f,
    diagnosis_group,
    cytoband_f,
    genes_f,
    gaps_f,
    ignore_cnv_f,
    roh_dirpath,
    false_pos_roh_gaps_f,
    cnvpytor_dirpath,
    coverage_dirpath,
    breakpoints_f,
    query_region,
    outdir,
):
    # gather samples based on the diagnosis grouping provided
    sample_list = get_samplelist(sample_config_f, diagnosis_group)
    print(f"No. of samples: {len(sample_list)}")

    # read sample name mapping
    samplename_map_dict = get_samplename_map(samplename_map_f)

    # controls subplots size as well as figure size
    extra_rows = 3
    nrows = len(sample_list) + extra_rows
    height_ratios = [3] * nrows
    height_ratios[0] = 4
    height_ratios[1] = 3
    height_ratios[2] = 6
    fig_height = sum(height_ratios) / 3.5
    if fig_height < 4:
        fig_height = 4

    fig, axes = plt.subplots(
        figsize=(10, fig_height),
        nrows=nrows,
        sharex=True,
        height_ratios=height_ratios,  # controls subplots height
    )

    # color configs
    colors_dict = define_colors()

    # read gaps data
    gaps_pr = read_gaps_data(gaps_f)

    # read CNVs to be ignored when drawing
    ignore_cnvs_dict = get_ignore_cnv_data(ignore_cnv_f)

    ##########  Cytoband  ##########
    # get cytoband data
    cytoband_df = read_cytoband_data(cytoband_f, query_region)

    # draw cytoband
    plot_patches(
        axes[0],
        cytoband_df,
        "cytoband",
        colors_dict["cytoband"],
        ylabel="Cytoband",
        annotation=True,
    )

    ##########  Breakpoints  ##########
    breakpoints_df = read_breakpoint_data(breakpoints_f, query_region)

    # draw breakpoints
    plot_patches(
        axes[1],
        breakpoints_df,
        "breakpoint",
        colors_dict["breakpoint"],
        ylabel="Breakpoints",
        annotation=True,
    )

    ##########  Genes  ##########
    # get genes data
    genes_df = read_genes_data(genes_f, query_region)

    # draw genes
    plot_patches(axes[2], genes_df, "genes", colors_dict["genes"], ylabel="Genes", annotation=True)

    # draw imprinted domain for chr15
    if query_region[0] == "chr15":
        # get imprinted genes
        imprinted_genes = genes_df.loc[
            genes_df["expression"].isin(["maternal", "paternal"]), :
        ].reset_index()
        imprint_region_start = imprinted_genes["Start"].iloc[0]
        imprint_region_end = imprinted_genes["End"].iloc[-1]

        # draw imprinted region
        axes[2].add_patch(
            patches.Rectangle(
                (imprint_region_start, 5.6),
                imprint_region_end - imprint_region_start,
                0.9,  # height
                edgecolor="cyan",
                linewidth=0.2,
                facecolor="cyan",
            )
        )
        axes[2].text(imprint_region_end + 30000, 6, "Imprinted domain", va="center")

    for i, sample in enumerate(sample_list):
        # print(sample, samplename_map_dict[sample])
        axes_no = i + extra_rows

        ##########  ROH  ##########
        # roh_f = Path(roh_dirpath) / f"{sample}.tsv"
        roh_f = Path(roh_dirpath.substitute(SAMPLE_NAME=sample)) / "filtered_ROH_blocks_with_qc.bed"
        roh_df = read_roh_data(roh_f, query_region, min_roh_mb=1.0)

        # plot roh
        plot_patches(
            axes[axes_no], roh_df, "roh", colors_dict["roh"], ylabel=samplename_map_dict[sample]
        )

        ##########  False positive ROH gaps  ##########
        fp_roh_gaps_df = read_falsePos_roh_gaps(false_pos_roh_gaps_f, query_region, sample)

        # plot fp roh gaps
        plot_patches(
            axes[axes_no],
            fp_roh_gaps_df,
            "fp_roh_gaps",
            colors_dict["fp_roh_gaps"],
            ylabel=samplename_map_dict[sample],
        )

        ##########  CNV  ##########
        binsize_cnvpytor = 10000
        cnv_f = (
            Path(cnvpytor_dirpath)
            / sample
            / f"cnvpytor/binsize_{binsize_cnvpytor}/calls_filtered_genotyped.tsv"
        )
        cnv_ignore_pr = ignore_cnvs_dict[sample] if sample in ignore_cnvs_dict else pr.PyRanges()
        cnv_df = read_cnv_data(cnv_f, gaps_pr, cnv_ignore_pr, query_region)

        # plot cnv
        plot_patches(
            axes[axes_no], cnv_df, "cnv", colors_dict["cnv"], ylabel=samplename_map_dict[sample]
        )

        ##########  Coverage  ##########
        mosdepth_f = Path(coverage_dirpath) / sample / f"{sample}.regions.bed.gz"
        coverage_df = read_coverage_data(mosdepth_f, query_region)

        plot_coverage(axes[axes_no], coverage_df)

    # Set xaxis limits and labelling
    axes[0].set_xlim(cytoband_df["Start"].min(), cytoband_df["End"].max())
    axes[nrows - 1].set_xlabel("Position", color="black")
    axes[nrows - 1].tick_params(axis="x", colors="black")

    # figure title
    fig_title = query_region[0]
    if len(query_region) > 1:
        fig_title += f": {query_region[1]:,} - {query_region[2]:,}"
    fig.suptitle(fig_title, fontsize=14)

    # time to save
    Path(outdir).mkdir(exist_ok=True, parents=True)
    outfile = Path(outdir) / f"{fig_title.replace(' ', '')}.png"
    fig.savefig(outfile, dpi=300)

    plt.close()

    return None


if __name__ == "__main__":
    SAMPLE_CONFIG_F = "configs/sample_diagnosis_grouping.yaml"  # see src/plot_roh_cnv.py for info on this file
    SAMPLENAME_MAP_F = "data/raw/Participant Paper IDs.tsv" # see src/plot_roh_cnv.py for info on this file
    CYTOBAND_F = "data/external/cytoband/cytoBand.txt.gz"   # see src/plot_roh_cnv.py for info on this file
    GENES_F = "data/raw/genes/hgnc_ucscTableBrowser_hg38_26jun2024_moreHighlights.bed"  # see src/plot_roh_cnv.py for info on this file
    BREAKPOINTS_F = "data/raw/pws_breakpoints.bed"  # see src/plot_roh_cnv.py for info on this file
    GAPS_F = "data/external/gaps/aggregated_gaps_hg38.bed"  # see src/plot_roh_cnv.py for info on this file
    IGNORE_CNV_F = "data/raw/ignore_cnv/ignore_cnv.tsv" # see src/plot_roh_cnv.py for info on this file

    QUERY_REGION_LIST = [
        # ("chr1",),
        # ("chr2",),
        # ("chr3",),
        # ("chr4",),
        # ("chr5",),
        # ("chr6",),
        # ("chr7",),
        # ("chr8",),
        # ("chr9",),
        # ("chr10",),
        # ("chr11",),
        # ("chr12",),
        # ("chr13",),
        # ("chr14",),
        ("chr15",),
        ("chr15", 20443169, 32600000),
        # ("chr16",),
        # ("chr17",),
        # ("chr18",),
        # ("chr19",),
        # ("chr20",),
        # ("chr21",),
        # ("chr22",),
        # ("chrX",),
        # ("chrY",),
    ]

    # see src/plot_roh_cnv.py for info on this file
    ROH_TIMESTAMP = "2024-06-04T10:10:54"
    ROH_DIRPATH = Template(
        f"/projects/PWS/analysis/$SAMPLE_NAME/roh_automap/{ROH_TIMESTAMP}/postprocessing"
    )
    FALSE_POS_ROH_GAPS_F = "data/raw/falsePos_ROH_gaps/falsePos_ROH_gaps.tsv"   # see src/plot_roh_cnv.py for info on this file

    # see src/plot_roh_cnv.py for info on this file
    CNVPYTOR_DIRPATH = "/projects/PWS/analysis/project_level_analysis/cnvpytor/PWS/analysis"

    # coverage calculated using mosdepth. See readme for how-to.
    COVERAGE_DIRPATH = "data/processed/mosdepth/chr15"

    for QUERY_REGION in QUERY_REGION_LIST:
        print(f"######### Query Region: {QUERY_REGION} #########")
        for DIAGNOSIS_GROUP in [
            "TypeI",
            "TypeII",
            # "TypeII_part1",
            # "TypeII_part2",
            "deletions",
            "deletions_cov_part2",
            "deletions_cov_part3",
            "UPD",
            # "all_samples",
            # "all_samples_group_sorted",
        ]:
            print(f"Working on diagnosos group: {DIAGNOSIS_GROUP}")
            OUTDIR = f"data/processed/python_viz/{strftime('%Y-%m-%d')}_cov/group_by_diagnosis/{DIAGNOSIS_GROUP}"

            main(
                SAMPLE_CONFIG_F,
                SAMPLENAME_MAP_F,
                DIAGNOSIS_GROUP,
                CYTOBAND_F,
                GENES_F,
                GAPS_F,
                IGNORE_CNV_F,
                ROH_DIRPATH,
                FALSE_POS_ROH_GAPS_F,
                CNVPYTOR_DIRPATH,
                COVERAGE_DIRPATH,
                BREAKPOINTS_F,
                QUERY_REGION,
                OUTDIR,
            )
        print("\n")
