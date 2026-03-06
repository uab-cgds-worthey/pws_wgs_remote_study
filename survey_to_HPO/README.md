# HPOs from PWS survey

Surveys (with >300 rows/fields) were collected from the PWS participants. Here, we systematically process these survey
responses and identify Human Phenotype Ontology (HPO) IDs relevant for each participant.

## Requirements

* conda

## Map HPO to survey fields

In the key file serving as data dictionary describing survey fields with their descriptions and valid respones, HPO IDs
were manually added using the criteria below, and the file was saved as `configs/survey_HPO_added.csv` (**TODO - mention
if this file is included in the repo or not after we decide on how to proceed**).

* Based on description in the `question text` column, appropriate HPO IDs were manually identified. Minority of them
 could be subjective or be using broader HPO terms.
* If no appropriate HPO term was available, `NA` was used.
* If a field was not a phenotype-related one, such as frequency or other quantitative fields, it was marked as
 `skip`.
* If a field maps to >1 HPO term, HPO IDs were added with string starting as `multiple HPO-`. For example, `multiple
 HPO-HP:0012210,HP:0000079`.
* If a field needs further computational logic to choose an appropriate HPO ID, it was marked as `special`.
* If a field needs manual review before choosing HPO IDs, it was marked as `manual`.

## How to run

```sh
# change into root directory of the repo
cd path/to/pws_survey_to_hpo

# create conda environment. Needed only the first time.
conda env create --file configs/envs/parse_survey.yaml

# activate conda environment
conda activate parse_survey

# run script
# see inline comments when calling main() in the script for necessary input requirements
python src/parse_survey/get_hpo_for_sample.py
```
