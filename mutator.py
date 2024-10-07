import argparse
import os
import re

from loguru import logger


def read_java_files(directory):
    java_files = {}
    for root, _, files in os.walk(directory):
        java_files.update({
            os.path.join(root, file): open(os.path.join(root, file), 'r').read()
            for file in files if file.endswith('.java')
        })
    return java_files


def extract_elements(java_code):
    try:
        # Regex patterns
        class_pattern = r'\bclass\s+(\w+)'
        function_pattern = r'\b(?:public|private|protected|static|\s) +[\w\<\>\[\]]+\s+(\w+) *\([^\)]*\) *\{'
        variable_pattern = r'\b(?:int|float|double|boolean|char|String)\s+(\w+)\s*[=;]'
        operation_pattern = r'(\+=|-=|\*=|/=|%=|\+\+|--|==|!=|>=|<=|&&|\|\||!)'
        operand_pattern = r'\b(\w+)\s*(?:\+=|-=|\*=|/=|%=|=|\+\+|--)'

        # Extract elements
        classes = re.findall(class_pattern, java_code)
        functions = re.findall(function_pattern, java_code)
        variables = re.findall(variable_pattern, java_code)

        # Extract operations and operands with their positions
        operations = [(m.group(1), m.start()) for m in re.finditer(operation_pattern, java_code)]
        operands = [(m.group(1), m.start()) for m in re.finditer(operand_pattern, java_code)]

        return {
            'classes': classes,
            'functions': functions,
            'variables': variables,
            'operations': operations,
            'operands': operands
        }
    except Exception as e:
        logger.opt(exception=True).error(f"Error extracting elements: {e}")

def replace_at_position(text, old_text, new_text, position):
    try:
        return text[:position] + text[position:].replace(old_text, new_text, 1)
    except Exception as e:
        logger.opt(exception=True).error(f"Error replacing text at position: {e}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", help="Directory containing Java files")
    args = parser.parse_args()

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