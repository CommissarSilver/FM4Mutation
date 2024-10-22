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


def parse_java_code(java_code):
    tokens = list(javalang.tokenizer.tokenize(java_code))
    parser = javalang.parser.Parser(tokens)

    try:
        tree = parser.parse_member_declaration()
        traverse_ast(tree, java_code)
    except javalang.parser.JavaSyntaxError as e:
        logger.error(f"Java syntax error while parsing: {e}")
    except Exception as e:
        logger.error(f"Unexpected error while parsing: {e}")


def extract_node_info(node, code_text):
    position = get_node_position(node)

    if position["line"] is not None and position["column"] is not None:
        start_index = get_index_from_position(
            code_text, position["line"], position["column"]
        )
    else:
        start_index = None

    if isinstance(node, javalang.tree.MethodDeclaration):
        extracted_elements["methods"].append(
            {
                "name": node.name,
                "parameters": [param.name for param in node.parameters],
                "position": position,
                "start_index": start_index,
            }
        )

    elif isinstance(node, javalang.tree.VariableDeclarator):
        extracted_elements["variables"].append(
            {"name": node.name, "position": position, "start_index": start_index}
        )

    elif isinstance(node, javalang.tree.BinaryOperation):
        operands = get_operands(node, code_text)
        extracted_elements["operations"].append(
            {
                "operation": node.operator,
                "operands": operands,
                "position": position,
                "start_index": start_index,
            }
        )


def get_node_position(node):
    if hasattr(node, "position") and node.position is not None:
        return {"line": node.position.line, "column": node.position.column}
    return {"line": None, "column": None}


def get_index_from_position(code_text, line, column):
    lines = code_text.splitlines()
    if line - 1 < len(lines):
        return sum(len(lines[i]) + 1 for i in range(line - 1)) + column - 1
    return None


def get_operands(node, code_text):
    operands = []
    if hasattr(node, "operandl") and node.operandl:
        if isinstance(node.operandl, javalang.tree.Literal) or isinstance(
            node.operandl, javalang.tree.MemberReference
        ):
            operands.append(str(node.operandl))
        else:
            operands.append(get_expression_text(node.operandl, code_text))
    if hasattr(node, "operandr") and node.operandr:
        if isinstance(node.operandr, javalang.tree.Literal) or isinstance(
            node.operandr, javalang.tree.MemberReference
        ):
            operands.append(str(node.operandr))
        else:
            operands.append(get_expression_text(node.operandr, code_text))
    return operands


def get_expression_text(node, code_text):
    position = get_node_position(node)
    if position["line"] is not None and position["column"] is not None:
        start_index = get_index_from_position(
            code_text, position["line"], position["column"]
        )
        return code_text[start_index : start_index + len(str(node))]
    return ""


def traverse_ast(node, code_text):
    extract_node_info(node, code_text)
    if hasattr(node, "children") and node.children is not None:
        for child in node.children:
            if isinstance(child, list):
                for sub_child in child:
                    traverse_ast(sub_child, code_text)
            elif child:
                traverse_ast(child, code_text)


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
    parse_java_code(project_details["code"])
    print("hi")


if __name__ == "__main__":
    main()
