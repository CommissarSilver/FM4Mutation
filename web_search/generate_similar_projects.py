import os
import json
import openai

# Set up OpenAI API key
openai.api_key = "YOUR_OPENAI_API"  # Replace with your actual API key


def load_json_files(input_dir):
    # """Load JSON files from a specified directory."""
    json_files = [f for f in os.listdir(input_dir) if f.endswith('.json')]
    for file in json_files:
        with open(os.path.join(input_dir, file), 'r') as f:
            data = json.load(f)
            yield file, data


def generate_bug_description(data):
    # """Generate a bug description using OpenAI's API based on the input JSON data."""
    prompt = f"""
    Generate a detailed bug description for the following data.

    Bug ID: {data.get("bug_id")}
    Project: {data.get("project")}

    Code:
    {data.get("code")}


    Please search on the web and provide me with five Java Projects that fits the following requirements:
    1. Can be compile and test locally.
    2. Contains a function with similar functionality to the code I provided above.
    3. Available on GitHub.
    
    Please provide your response in the following format:
    ```
    Project 1
    Program name:
    Program link:
    Program similar function name:
    Program similar function location:
    
    Project 2
    """

    try:
        response = openai.chat.completions.create(
            model="chatgpt-4o-latest", #gpt-4o
            messages=[{"role": "user", "content": prompt}],
            # max_tokens=6000,
            temperature=1.0
        ).model_dump_json()
        response = json.loads(response)
        bug_description = [choice['message']['content'] for choice in response['choices']][0]
        return bug_description
    except Exception as e:
        print(f"Error generating description: {e}")
        return None


def process_json_files(input_dir, output_dir):
    # """Process JSON files to generate bug descriptions for 'SF' bug types and save modified files."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for file_name, data in load_json_files(input_dir):
        # if os.path.exists(os.path.join(output_dir, file_name)):
        #     print(f"Skipping {file_name}, directory exists.")
        #     continue
        if "bug_description" in data:
            print(f"Skipping {file_name}, bug_description.")
            continue
        if "SF" in data.get("bug_type"):
            bug_description = generate_bug_description(data)
            if bug_description:
                data["bug_description"] = bug_description

            new_file_name = file_name.split('.')[0] + '.txt'
            # Save modified JSON to the output directory
            with open(os.path.join(output_dir, new_file_name), 'w') as f:
                f.write(bug_description)
            print(f"Processed and saved: {file_name}")
        else:
            print(f"Skipping {file_name}, bug_type is not SF.")


# Example usage
input_directory = "../cache/bug_details_cache"  # Replace with your actual input directory path
output_directory = "./1"  # Replace with your actual output directory path
process_json_files(input_directory, output_directory)

