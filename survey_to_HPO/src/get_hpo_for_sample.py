from pathlib import Path

import networkx
import obonet
import pandas as pd
import parse_survey_fields


def get_hpo_superterms(hpo_id, graph, id_to_name):
    "identify system level ancestor HPO for the query HPO. Some may have more than 1."

    system_level_hpo_list = [
        "Abnormality of the musculoskeletal system",
        "Abnormality of limbs",
        "Abnormality of the nervous system",
        "Abnormality of metabolism/homeostasis",
        "Abnormality of the genitourinary system",
        "Abnormality of head or neck",
        "Abnormality of the cardiovascular system",
        "Abnormality of the eye",
        "Abnormality of the immune system",
        "Abnormality of the integument",
        "Abnormality of blood and blood-forming tissues",
        "Abnormality of the digestive system",
        "Neoplasm",
        "Abnormality of the respiratory system",
        "Abnormality of the endocrine system",
        "Abnormality of the ear",
        "Abnormal cellular phenotype",
        "Abnormality of prenatal development or birth",
        "Constitutional symptom",
        "Growth abnormality",
        "Abnormality of the breast",
        "Abnormality of the voice",
        "Abnormality of the thoracic cavity",
    ]

    hpo_label = id_to_name[hpo_id]
    superterms = [id_to_name[superterm] for superterm in networkx.descendants(graph, hpo_id)]
    # print(superterms)

    system_hpo = sorted(list(set(superterms).intersection(set(system_level_hpo_list))))
    if len(system_hpo) < 1:
        print(f"No system level HPO found for {hpo_id}, {hpo_label}")
        raise SystemExit(1)

    return system_hpo, hpo_label


def get_apnea_type(text):

    text = text.lower()

    matches = ("apnea", "know", "normal", "nan")
    if not any(x in text for x in matches):
        print(f"ERROR: None of the expected substrings '{matches}' present: '{text}'")
        raise SystemExit()

    hpo = []
    if "obstructive" in text:
        hpo.append("HP:0002870")
        # hpo.append("obstructive")

    if "central" in text:
        hpo.append("HP:0010536")
        # hpo.append("central")

    if "apnea, but i don't know what kind" in text:
        hpo.append("HP:0010535")
        # hpo.append("apnea")

    return hpo


def is_puberty_delayed(text, menstruation_dict):

    sex = menstruation_dict["sex"]
    current_age = menstruation_dict["current_age"]
    menstruation_status = text.lower()
    menstruation_age = menstruation_dict["menstruation_age"]

    if sex not in ["male", "female"]:
        print(f"Error. Sample's sex not expected: '{sex}'")

    if sex == "female":
        threshold = 15
        if current_age > threshold:
            if menstruation_status.lower() == "yes":
                if menstruation_age > threshold:
                    menstruation_delay = True
                else:
                    menstruation_delay = False
            elif menstruation_status.lower() == "no":
                menstruation_delay = True
            else:
                print("Error: Unexpected scenario. May need logic check and modification.")
                raise SystemExit(1)
        else:
            menstruation_delay = False

        if menstruation_delay:
            return ["HP:0012569"]
    else:
        return []


def get_hpo_id(
    hpo_id_from_file,
    field_info_dict,
    field,
    choice,
    special_hpo_dict,
    needs_manual_review,
    menstruation_dict,
):
    "gets HPO IDs relevant for the survey field"

    hpo_id_list = []
    if hpo_id_from_file.startswith("HP:"):
        hpo_id_list = [hpo_id_from_file]
    elif hpo_id_from_file.startswith("multiple HPO"):
        hpo_id_list = field_info_dict[field]["hpo_id"].split("-")[1].split(",")
    elif hpo_id_from_file == "special":
        if field == "endocrinological_history.endocrine_diagnosis_thyroid_type":
            if "hypothyroidism" in choice.lower():
                hpo_id_list = ["HP:0000821"]
            elif "hyperthyroidism" in choice.lower():
                hpo_id_list = ["HP:0000836"]
            else:
                pass
        elif field == "endocrinological_history.endocrine_diagnosis_diabetes_type":
            # if not pd.isnull(choice):
            if choice:
                if "type 1 diabetes" in choice.lower():
                    hpo_id_list = ["HP:0100651"]
                elif "type 2 diabetes" in choice.lower():
                    hpo_id_list = ["HP:0005978"]
                elif "pre-diabetic" in choice.lower():
                    hpo_id_list = ["HP:0000855", "HP:0001952"]
                else:
                    pass
        elif field == "orthopedic_history.orthopedic_diagnosis_spinal_deformity":
            # as per note: kyphosis and lordosis definitions are switched - cannot use these subtypes. Only scoliosis is used.
            if "scoliosis" in choice.lower():
                special_hpo_dict["scoliosis_present"] = True
            else:
                special_hpo_dict["scoliosis_present"] = False
        elif field == "orthopedic_history.orthopedic_diagnosis_spinal_deformity_scoliosis_type":
            if special_hpo_dict["scoliosis_present"]:
                if "thoracic curve" in choice.lower():
                    hpo_id_list = ["HP:0002943"]
                elif "thoracolumbar curve" in choice.lower():
                    hpo_id_list = ["HP:0002944"]
                elif "double major curve" in choice.lower():
                    # didn't find HPO for "double major curve". So using HPO for scoliosis
                    hpo_id_list = ["HP:0002650"]
        elif field in [
            "HQ-CT Total Score (Questions 1-9, Upset being denied food - Interfere Daily Activities)"
        ]:
            if int(choice) > 2:  # see readme.md about this threshold
                hpo_id_list = ["HP:0002591"]
        elif field in [
            "PWS Anxiousness and Distress Questionnaire Total Score (Questions 1-15)",
            "PADQ Total Score (Questions 1-15)",
        ]:
            if int(choice) > 5:  # see readme.md about this threshold
                hpo_id_list = ["HP:0000739"]
        elif field == "sleep_history.sleep_study_results":
            hpo_id_list = get_apnea_type(choice)
        elif field == "sexual_and_reproductive_history.sexual_menstruation":
            hpo_id_list = is_puberty_delayed(choice, menstruation_dict)

    elif hpo_id_from_file in ["manual"]:
        needs_manual_review.append((field_info_dict[field]["question_text"], choice))
    elif hpo_id_from_file in ["skip", "NA"]:
        pass
    else:
        print(f"Unexpected term in HPO column - {hpo_id_from_file}")
        raise SystemExit(1)

    return hpo_id_list


def main(survey_desc_f, choice_config_f, hpo_f, samples_response_dir, out_dir):

    # read hpo database
    graph = obonet.read_obo(hpo_f)
    hpo_id_to_name = {id_: data.get("name") for id_, data in graph.nodes(data=True)}

    for i, sample_response_f in enumerate(Path(samples_response_dir).glob("*.xlsx")):

        print(f"{i+1}. Sample survey response input: {str(sample_response_f)}")

        # read sample survey results
        sample_df = pd.read_excel(
            sample_response_f, index_col="Participant ID", names=["Participant ID", "sample"]
        )

        # get survey field mapping to its metadata
        field_info_dict = parse_survey_fields.main(survey_desc_f, choice_config_f)

        # gather info in a dict to help with puberty delay identificatoin logic
        menstruation_dict = {
            "sex": sample_df.loc["getting_started.pt_sex", "sample"].lower(),
            "current_age": sample_df.loc["getting_started.current_age", "sample"],
            "menstruation_age": sample_df.loc[
                "sexual_and_reproductive_history.sexual_menstruation_started_age_years", "sample"
            ],
        }

        hpo_ids = set()
        special_hpo_dict = {}
        needs_manual_review = []
        for field, row in sample_df.iterrows():
            choice = str(row[0]).strip()
            if field not in field_info_dict:
                # some samples' survey have typo in the field name. So make it right.
                if field == "psychological_and_mental_health.psych_behavior_psychosi":
                    field = "psychological_and_mental_health.psych_behavior_psychosis"
                # exit if field not among the expected
                else:
                    print(
                        f"Field '{field}' expected but not present in {survey_desc_f}. Exiting now..."
                    )
                    raise SystemExit(1)

            hpo_id_from_file = field_info_dict[field]["hpo_id"]
            hpo_term_from_file = field_info_dict[field]["hpo_term"]

            # get hpo IDs
            hpo_id_list = get_hpo_id(
                hpo_id_from_file,
                field_info_dict,
                field,
                choice,
                special_hpo_dict,
                needs_manual_review,
                menstruation_dict,
            )
            if not hpo_id_list:
                continue

            for hpo_id in hpo_id_list:
                if hpo_id_from_file == "special":
                    pass
                elif choice not in field_info_dict[field]["choices_to_include"]:
                    continue

                # identify which system level parent HPO ID belongs to.
                system_hpo, hp_label_from_obo = get_hpo_superterms(hpo_id, graph, hpo_id_to_name)

                if not hpo_term_from_file:
                    hpo_term = hp_label_from_obo
                else:
                    hpo_term = hpo_term_from_file

                hpo_ids.add(("; ".join(system_hpo), hpo_id, hpo_term))
                del hpo_term

        Path(out_dir).mkdir(exist_ok=True, parents=True)
        out_f = Path(out_dir) / f"{sample_response_f.stem}.tsv"
        with open(out_f, "w") as out_handle:
            out_handle.write(
                f"# HPOs identified programmatically. Based on '{sample_response_f}'\n"
            )
            for hpo in sorted(hpo_ids):
                out_handle.write("\t".join([hpo[1], hpo[2], hpo[0]]) + "\n")

            out_handle.write("# Below are HPOs added manually\n")
            for item in needs_manual_review:
                out_handle.write(f"{item[0]}: '{item[1]}'\n")

    return None


if __name__ == "__main__":
    SURVEY_HPO_F = "configs/survey_HPO_added.csv"   # survey key file with manually added HPO related info; example file provided at this path.
    CHOICES_CONFIG_F = "configs/choice_values_to_include.json"  # informs how to process field choices
    HPO_F = "data/external/hp_12feb2022.obo"    # HPO dataset from https://hpo.jax.org/data/ontology
    SAMPLES_RESPONSE_INDIR = "data/interim/sample_survey_response"    # contains participant survey response files in xlsx format; not included in the repo.
    OUT_DIR = "data/processed/sample_hpo/programmatic_output"
    main(SURVEY_HPO_F, CHOICES_CONFIG_F, HPO_F, SAMPLES_RESPONSE_INDIR, OUT_DIR)
