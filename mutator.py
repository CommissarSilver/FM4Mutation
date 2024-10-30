import argparse
import os
import json
from loguru import logger
import random
import subprocess

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

extracted_elements = {"classes": [], "methods": [], "variables": [], "operations": []}
mapping = {
    "project": args.project,
    "mutation": args.mutation,
    "number_of_mutants": args.number_of_mutants,
    "original_lines": None,
    "mutated_lines": None,
    "mutated_files": None,
}


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


def find_fixed_lines_indices(code, fixed_lines):
    fixed_lines_indices = []
    code_lines = code.splitlines()
    for fixed_line in fixed_lines:
        for i, line in enumerate(code_lines):
            if fixed_line in line:
                fixed_lines_indices.append(i)
                break
    return fixed_lines_indices


def mutate_fixed_lines(code, fixed_lines_indices):
    code_lines = code.splitlines()

    line = code_lines[fixed_lines_indices]
    mutated_line = mutate_line(line)
    mapping["mutated_lines"] = mutated_line
    code_lines[fixed_lines_indices] = mutated_line
    return "\n".join(code_lines)


def mutate_line(line):
    # Example mutation: replace '==' with '!='
    return line.replace("==", "!=")


def main():
    project_details = json.load(
        open(
            os.path.join(
                args.cache_dir,
                f"{args.project}.json",
            ),
            "r",
        )
    )
    fixed_lines = project_details.get("fixed_lines", "").split("\n")
    code = project_details["fixed_code"]

    fixed_lines_indices = find_fixed_lines_indices(code, fixed_lines)
    indice_to_change = random.choice(fixed_lines_indices)
    mapping["original_lines"] = code.splitlines()[indice_to_change]

    mutated_code = mutate_fixed_lines(code, indice_to_change)
    mapping["mutated_files"] = mutated_code

    if args.store:
        save_mutated_file(args.project, mutated_code)

    print(mutated_code)


if __name__ == "__main__":
    main()
