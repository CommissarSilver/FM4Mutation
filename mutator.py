import argparse
import os
import re
import json
from loguru import logger
import javalang

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
    default=False,
    help="Whether to store the mutated files in defects4j",
)
args = parser.parse_args()

extracted_elements = {"classes": [], "methods": [], "variables": [], "operations": []}


def save_mutated_file(original_path, mutated_content):
    directory, filename = os.path.split(original_path)
    name, _ = os.path.splitext(filename)
    new_filename = f"{name}_mutated.java"
    new_path = os.path.join(directory, new_filename)

    counter = 1
    while os.path.exists(new_path):
        new_filename = f"{name}_mutated_{counter}.java"
        new_path = os.path.join(directory, new_filename)
        counter += 1

    with open(new_path, "w") as f:
        f.write(mutated_content)

    return new_path


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
    for index in fixed_lines_indices:
        line = code_lines[index]
        mutated_line = mutate_line(line)
        code_lines[index] = mutated_line
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
    code = project_details["code"]

    fixed_lines_indices = find_fixed_lines_indices(code, fixed_lines)
    mutated_code = mutate_fixed_lines(code, fixed_lines_indices)

    if args.store:
        save_mutated_file(args.project, mutated_code)

    print(mutated_code)


if __name__ == "__main__":
    main()
