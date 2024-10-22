import os
import json
import csv

# Define the list of bugs
d4j_list_of_bugs = [("Cli", [i for i in range(1, 41) if i != 6]),
                    ("Codec", [i for i in range(1, 19)]),
                    ("Collections", [i for i in range(25, 29)]),
                    ("Compress", [i for i in range(1, 48)]),
                    ("Csv", [i for i in range(1, 17)]),
                    ("Gson", [i for i in range(1, 19)]),
                    ("JacksonCore", [i for i in range(1, 27)]),
                    ("JacksonDatabind", [i for i in range(1, 113)]),
                    ("Jsoup", [i for i in range(1, 94)]),
                    ("JxPath", [i for i in range(1, 23)])]

# Extract the first element of each group
project_prefixes = [group[0] for group in d4j_list_of_bugs]

# Define the directory containing JSON files and the output CSV file path
input_directory = "./bug_details_cache"  # Replace with the path to your JSON files
output_csv = "output.csv"  # Replace with the desired output CSV file path

# List to store file names without .json extension
filtered_files = []

# Iterate through each file in the input directory
for filename in os.listdir(input_directory):
    if filename.endswith(".json"):
        # Check if the file starts with any of the project prefixes
        for prefix in project_prefixes:
            if filename.startswith(prefix):
                # Read the JSON file
                file_path = os.path.join(input_directory, filename)
                with open(file_path, 'r') as file:
                    data = json.load(file)
                    # Check if "bug_type" contains "SF"
                    if data.get("bug_type") != "OT":
                        # Remove the .json extension and add to the list
                        filtered_files.append(filename.replace(".json", ""))

# Write the filtered file names to the CSV file
with open(output_csv, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["File Names"])  # Header
    for file_name in filtered_files:
        writer.writerow([file_name])

print(f"Filtered file names have been saved to {output_csv}")

