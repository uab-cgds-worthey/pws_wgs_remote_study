import csv
import json


def get_survey_field_mapping(survey_desc_f, choices_to_keep):

    field_info_dict = {}
    with open(survey_desc_f, encoding="utf-8-sig") as f_handle:
        data = csv.DictReader(f_handle)
        for i, row in enumerate(data):
            field = row["field"]
            clinical_feature = row["Clinical Feature this Question is assessing"]
            choice = row["Choices"].strip()

            field_info_dict[field] = {
                "survey": row["Survey"],
                "clinical_feature": clinical_feature,
                "question_text": row["Question Text"],
                "variable_field_name": row["Variable Field Name"],
                "all_choices": choice,
                "choices_to_include": choices_to_keep.get(choice, {}),
                "hpo_id": row["HPO_ID"],
                "hpo_term": row["HPO_TERM"],
            }

    # Account for alternative field name
    field_info_dict[
        "PWS Anxiousness and Distress Questionnaire Total Score (Questions 1-15)"
    ] = field_info_dict["PADQ Total Score (Questions 1-15)"]


    return field_info_dict


def get_inclusion_choices(f):

    with open(f, "r") as f_handle:
        data = json.load(f_handle)

    return data


def main(survey_desc_f, choice_config_f):

    # choices to be included - hpo id will be fetched only if these choices are used
    choices_to_keep = get_inclusion_choices(choice_config_f)

    # map survey field to the metadata and descriptions
    field_info_dict = get_survey_field_mapping(survey_desc_f, choices_to_keep)

    return field_info_dict


if __name__ == "__main__":
    SURVEY_F = "configs/survey_HPO_added.csv"

    CHOICES_CONFIG_F = "configs/choices_to_include.json"
    main(SURVEY_F, CHOICES_CONFIG_F)
