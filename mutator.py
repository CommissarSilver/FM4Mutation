import re
import os

def read_java_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()

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
    java_file_path = input("Enter the path to the Java file: ")
    
    if not os.path.exists(java_file_path):
        print("File not found!")
        return

    java_code = read_java_file(java_file_path)
    elements = extract_elements(java_code)

    print("\nExtracted elements:")
    for key, value in elements.items():
        if key in ['classes', 'functions', 'variables']:
            print(f"{key.capitalize()}: {', '.join(value)}")
        else:
            print(f"{key.capitalize()}:")
            for item, pos in value:
                print(f"  '{item}' at position {pos}")

    # Choose what to modify
    modify_type = input("\nDo you want to modify an 'operation' or an 'operand'? ").lower()
    if modify_type not in ['operation', 'operand']:
        print("Invalid choice. Exiting.")
        return

    # List available choices
    choices = elements[modify_type + 's']  # Add 's' to get the correct key
    for i, (item, pos) in enumerate(choices):
        print(f"{i}: '{item}' at position {pos}")

    # Get user choice
    choice_index = int(input(f"Enter the number of the {modify_type} you want to modify: "))
    if choice_index < 0 or choice_index >= len(choices):
        print("Invalid choice. Exiting.")
        return

    old_item, position = choices[choice_index]
    new_item = input(f"Enter the new {modify_type}: ")

    # Modify the code
    modified_code = replace_at_position(java_code, new_item, position)

    # Save the modified code
    output_path = java_file_path.rsplit('.', 1)[0] + '_modified.java'
    with open(output_path, 'w') as file:
        file.write(modified_code)

    print(f"\nModified code saved to: {output_path}")

if __name__ == "__main__":
    main()