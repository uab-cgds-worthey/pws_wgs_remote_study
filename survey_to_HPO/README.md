# Build HPO profile for participants from their PWS survey

Surveys (with >300 rows/fields) were collected from PWS participants. Here, we systematically process these survey
responses and build participant-specific phenotype profile using Human Phenotype Ontology (HPO).

## Map survey questions/fields to HPO

Each field/question in the survey was manually mapped to HPO IDs using the following criteria:

* Based on description in the `question text` column, appropriate HPO IDs were manually identified. Minority of them
 could be subjective or be using broader HPO terms.
* If no appropriate HPO term was available, `NA` was used.
* If a field was not a phenotype-related one, such as frequency or other quantitative fields, it was marked as `skip`.
* If a field maps to >1 HPO term, HPO IDs were added with string starting as `multiple HPO-`. For example, `multiple
 HPO-HP:0012210,HP:0000079`.
* If a field needs further computational logic to choose an appropriate HPO ID, it was marked as `special`.
* If a field needs manual review before choosing HPO IDs, it was marked as `manual`.

Survey fields along with the added HPO IDs were saved in `configs/survey_HPO_added.csv`. Note that only a small subset
of rows in this file is included in this repo, to demonstrate its file structure.

## Requirements

* conda (v23+)

## How to run

```sh
# change into directory
cd survey_to_HPO

# create conda environment. Needed only the first time.
conda env create --file configs/envs/parse_survey.yaml

# activate conda environment
conda activate parse_survey

# run script
# see inline comments when calling main() in the script for necessary data/input requirements
python src/get_hpo_for_sample.py
```
