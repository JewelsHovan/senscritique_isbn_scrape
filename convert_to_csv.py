# convert scraped data from json format to csv

import json
import csv

def flatten_json(json_obj):
    # Convert list values to comma-separated strings
    flattened = {}
    for key, value in json_obj.items():
        if isinstance(value, list):
            flattened[key] = "|".join(str(v) for v in value)
        else:
            flattened[key] = value
    return flattened

def convert_json_to_csv(json_file, csv_file):
    # Read JSON data
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Handle both single object and list of objects
    if not isinstance(data, list):
        data = [data]
    
    # Flatten each JSON object
    flattened_data = [flatten_json(item) for item in data]
    
    # Write to CSV
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=flattened_data[0].keys())
        writer.writeheader()
        writer.writerows(flattened_data)


if __name__ == "__main__":
    json_file = "books_data.json"
    csv_file = "books_data.csv"
    convert_json_to_csv(json_file, csv_file)
    print(f"Data has been successfully converted to {csv_file}")