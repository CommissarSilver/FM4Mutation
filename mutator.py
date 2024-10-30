import argparse
import json
import os
import re
import xml.etree.ElementTree as ET

from loguru import logger

from llm_interface import LLMInterface

parser = argparse.ArgumentParser()
parser.add_argument(
    "--cache_dir",
    type=str,
    default=os.path.join(os.getcwd(), "cache", "bug_details_cache"),
    help="Path to the json cache directory",
)
parser.add_argument(
    "--project",
    type=str,
    default="Cli-11",
    help="Project name [e.g., Chart, Cli, etc.]",
)
parser.add_argument(
    "--mutation",
    type=str,
    default="AOD",
    help="Mutation operator [e.g., AOD, AOR, etc.]",
)
parser.add_argument(
    "--number_of_mutants",
    type=int,
    default=1,
    help="Number of mutants to generate",
)
parser.add_argument(
    "--store",
    type=bool,
    default=True,
    help="Whether to store the mutated files in defects4j",
)
args = parser.parse_args()

if args.store:
    if not os.path.exists(os.path.join(os.getcwd(), "mutated_codes")):
        os.makedirs(os.path.join(os.getcwd(), "mutated_codes"))

    mutated_files_dir = os.path.join(os.getcwd(), "mutated_codes")


def save_mutated_file(mutated_content: str, mutation_num: int):
    original_json = json.load(
        open(
            os.path.join(
                args.cache_dir,
                f"{args.project}.json",
            ),
            "r",
        )
    )
    original_json["code"] = mutated_content
    original_json["bug_id"] = mutation_num
    with open(
        os.path.join(
            mutated_files_dir,
            f"{args.project}_{args.mutation}_{mutation_num}.json",
        ),
        "w",
    ) as f:
        json.dump(original_json, f, indent=4)

    logger.info(
        f"Mutated file saved successfully at: {mutated_files_dir}/{args.project}_{args.mutation}_{mutation_num}.json"
    )


def save_data_trail(
    original_code: str,
    mutated_code: str,
    mutation_type: str,
    model: str,
    prompt: str,
    mutation_details: dict,
    trail_num: int,
):
    data_trail = {
        "original_code": original_code,
        "mutated_code": mutated_code,
        "mutation_type": mutation_type,
        "model": model,
        "prompt": prompt,
        "mutation_details": mutation_details,
    }
    trail_file_path = os.path.join(mutated_files_dir, f"data_trail_{trail_num}.json")
    with open(trail_file_path, "w") as f:
        json.dump(data_trail, f, indent=4)
    logger.info(f"Data trail saved successfully at: {trail_file_path}")


def parse_llm_output(xml_output: str) -> dict:
    try:
        # Extract the <mutation_result> section using regex
        match = re.search(
            r"<mutation_result>(.*?)</mutation_result>", xml_output, re.DOTALL
        )
        if not match:
            logger.error("No <mutation_result> found in LLM output")
            return {}

        mutation_result_xml = f"<mutation_result>{match.group(1)}</mutation_result>"
        root = ET.fromstring(mutation_result_xml)

        mutation_result = {}
        for elem in root:
            if elem.tag == "mutation_details":
                mutation_result["mutation_details"] = {
                    child.tag: child.text.strip() for child in elem
                }
            else:
                # Handle CDATA sections
                if (
                    elem.text
                    and elem.text.startswith("<![CDATA[")
                    and elem.text.endswith("]]>")
                ):
                    mutation_result[elem.tag] = elem.text[9:-3].strip()
                else:
                    mutation_result[elem.tag] = elem.text.strip()
        return mutation_result
    except ET.ParseError as e:
        logger.error(f"Failed to parse XML output: {e}")
        return {}


def main():
    try:
        mutator = LLMInterface(config_file_path="agent_config.yml", verbose=False)
        mutator.set_role("mutator")
    except Exception as e:
        logger.opt(exception=True).error(f"Unable to instantiate LLMInterface: {e}")
        exit(1)

    try:
        project_details = json.load(
            open(
                os.path.join(
                    args.cache_dir,
                    f"{args.project}.json",
                ),
                "r",
            )
        )
        code_to_mutate = project_details.get("code", "")
    except Exception as e:
        logger.opt(exception=True).error(f"Unable to load project details: {e}")
        exit(1)

    try:
        mutated_code_xml = mutator.interact(mutation=args.mutation, code=code_to_mutate)
        mutation_data = parse_llm_output(mutated_code_xml)
        mutated_code = mutation_data.get("mutated_code", "")
        mutation_details = mutation_data.get("mutation_details", {})
    except Exception as e:
        logger.opt(exception=True).error(f"Unable to mutate code: {e}")
        exit(1)
    if args.store:
        save_mutated_file(mutated_code, 1)
        save_data_trail(
            original_code=code_to_mutate,
            mutated_code=mutated_code,
            mutation_type=args.mutation,
            model=mutator.llm.model_name,
            prompt=mutator.system_prompt,
            mutation_details=mutation_details,
            trail_num=1,
        )
    import pprint

    pprint.pprint(mutated_code)


if __name__ == "__main__":
    main()
