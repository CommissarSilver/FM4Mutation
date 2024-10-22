import argparse
import os
import re

from loguru import logger

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
    default="Cli-1",
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


def read_java_files(directory):
    java_files = {}
    for root, _, files in os.walk(directory):
        java_files.update(
            {
                os.path.join(root, file): open(os.path.join(root, file), "r").read()
                for file in files
                if file.endswith(".java")
            }
        )
    return java_files


def extract_elements(java_code):
    try:
        # Regex patterns
        class_pattern = r"\bclass\s+(\w+)"
        function_pattern = r"\b(?:public|private|protected|static|\s) +[\w\<\>\[\]]+\s+(\w+) *\([^\)]*\) *\{"
        variable_pattern = r"\b(?:int|float|double|boolean|char|String)\s+(\w+)\s*[=;]"
        operation_pattern = r"(\+=|-=|\*=|/=|%=|\+\+|--|==|!=|>=|<=|&&|\|\||!)"
        operand_pattern = r"\b(\w+)\s*(?:\+=|-=|\*=|/=|%=|=|\+\+|--)"

        # Extract elements
        classes = re.findall(class_pattern, java_code)
        functions = re.findall(function_pattern, java_code)
        variables = re.findall(variable_pattern, java_code)

        # Extract operations and operands with their positions
        operations = [
            (m.group(1), m.start()) for m in re.finditer(operation_pattern, java_code)
        ]
        operands = [
            (m.group(1), m.start()) for m in re.finditer(operand_pattern, java_code)
        ]

        return {
            "classes": classes,
            "functions": functions,
            "variables": variables,
            "operations": operations,
            "operands": operands,
        }
    except Exception as e:
        logger.opt(exception=True).error(f"Error extracting elements: {e}")


def replace_at_position(text, old_text, new_text, position):
    try:
        return text[:position] + text[position:].replace(old_text, new_text, 1)
    except Exception as e:
        logger.opt(exception=True).error(f"Error replacing text at position: {e}")


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


def main():

    if not os.path.isdir(args.directory):
        print("The specified path is not a directory.")
        return

    java_files = read_java_files(args.directory)

    if not java_files:
        logger.info("No Java files found.")
        return
    else:
        logger.info(f"Found {len(java_files)} Java files.")


if __name__ == "__main__":
    main()
