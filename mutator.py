import re
import os
import argparse

def read_java_files(directory):
    java_files = {}
    for root, _, files in os.walk(directory):
        java_files.update({
            os.path.join(root, file): open(os.path.join(root, file), 'r').read()
            for file in files if file.endswith('.java')
        })
    return java_files


def extract_elements(java_code):
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

def replace_at_position(text, new_text, position):
    return text[:position] + new_text + text[position + len(new_text):]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", help="Directory containing Java files")
    args = parser.parse_args()

    if not os.path.isdir(args.directory):
        print("The specified path is not a directory.")
        return

    java_files = read_java_files(args.directory)

    if not java_files:
        print("No Java files found in the specified directory.")
        return

    print(f"Found {len(java_files)} Java files.")

    # Process each Java file
    for file_path, java_code in java_files.items():
        print(f"\nProcessing file: {file_path}")
        elements = extract_elements(java_code)

        print("Extracted elements:")
        for key, value in elements.items():
            if key in ['classes', 'functions', 'variables']:
                print(f"{key.capitalize()}: {', '.join(value)}")
            else:
                print(f"{key.capitalize()}:")
                for item, pos in value:
                    print(f"  '{item}' at position {pos}")

        # Modify file if user wants
        if input("\nDo you want to modify this file? (y/n): ").lower() == 'y':
            modify_type = input("Do you want to modify an 'operation' or an 'operand'? ").lower()
            if modify_type not in ['operation', 'operand']:
                print("Invalid choice. Skipping this file.")
                continue

            choices = elements[modify_type + 's']
            for i, (item, pos) in enumerate(choices):
                print(f"{i}: '{item}' at position {pos}")

            choice_index = int(input(f"Enter the number of the {modify_type} you want to modify: "))
            if choice_index < 0 or choice_index >= len(choices):
                print("Invalid choice. Skipping this file.")
                continue

            old_item, position = choices[choice_index]
            new_item = input(f"Enter the new {modify_type}: ")

            # Modify the code
            modified_code = replace_at_position(java_code, new_item, position)

            # Save the modified code
            output_path = file_path.rsplit('.', 1)[0] + '_modified.java'
            with open(output_path, 'w') as file:
                file.write(modified_code)

            print(f"Modified code saved to: {output_path}")

if __name__ == "__main__":
    main()