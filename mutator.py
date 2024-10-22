import argparse
import os
import re
import json
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




def extract_elements(java_code):
    try:
        # Regex patterns
        class_pattern = r"\bclass\s+(\w+)"
        function_pattern = r"\b(?:public|private|protected|static|\s)*(?:<\w+>)?\s*[\w\<\>\[\]]+\s+(\w+)\s*\([^\)]*\)\s*\{"
        variable_pattern = r"\b(?:int|float|double|boolean|char|String|long|short|byte)\s+(\w+)\s*(?:=.*?)?\s*[;,]"
        operation_pattern = r"(\+=|-=|\*=|/=|%=|\+\+|--|==|!=|>=|<=|&&|\|\||!)"
        operand_pattern = (
            r"\b(\w+)\s*(?:\+|\-|\*|\/|\=|\+\+|\-\-)?(?:=|\+|\-|\*|\/|\%)?"
        )

        # Extract elements
        classes = re.findall(class_pattern, java_code)
        functions = re.findall(function_pattern, java_code)
        variables = re.findall(variable_pattern, java_code)

        classes = [
            (m.group(0), m.start()) for m in re.finditer(class_pattern, java_code)
        ]
        functions = [
            (m.group(0), m.start()) for m in re.finditer(function_pattern, java_code)
        ]
        variables = [
            (m.group(0), m.start()) for m in re.finditer(variable_pattern, java_code)
        ]
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
    project_details = json.load(
        open(
            os.path.join(
                args.cache_dir,
                f"{args.project}.json",
            ),
            "r",
        )
    )
    code_elements = extract_elements(project_details["code"])
    print("hi")


if __name__ == "__main__":
    main()
