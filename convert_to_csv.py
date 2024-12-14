# convert scraped data from json format to csv

import json
import csv

def flatten_json(json_obj):
    """
    Maps JSON data to Goodreads CSV format, with specific required columns.
    Returns a flattened dictionary with Goodreads-compatible fields.
    """
    # Define Goodreads columns
    goodreads_format = {
        'Title': '',
        'Author': '',
        'ISBN': '',
        'My Rating': '',
        'Average Rating': '',
        'Publisher': '',
        'Binding': '',
        'Year Published': '',
        'Original Publication Year': '',
        'Date Read': '',
        'Date Added': '',
        'Shelves': '',
        'Bookshelves': '',
        'My Review': ''
    }
    
    # Map known fields from json_obj to Goodreads format
    goodreads_format['Title'] = json_obj.get('title', '')
    # Handle author(s) - join multiple authors with comma if it's a list
    authors = json_obj.get('author', '')
    if isinstance(authors, list):
        goodreads_format['Author'] = ', '.join(authors)
    else:
        goodreads_format['Author'] = authors
    
    goodreads_format['ISBN'] = json_obj.get('isbn', '')
    goodreads_format['Year Published'] = json_obj.get('year', '')
    
    # Optional: map any additional fields if they exist in your JSON
    goodreads_format['Publisher'] = json_obj.get('publisher', '')
    
    return goodreads_format

def convert_json_to_csv(json_file, csv_file):
    # Read JSON data
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Handle both single object and list of objects
    if not isinstance(data, list):
        data = [data]
    
    # Flatten each JSON object using Goodreads format
    flattened_data = [flatten_json(item) for item in data]
    
    # Write to CSV with Goodreads columns
    goodreads_columns = ['Title', 'Author', 'ISBN', 'My Rating', 'Average Rating', 
                        'Publisher', 'Binding', 'Year Published', 'Original Publication Year',
                        'Date Read', 'Date Added', 'Shelves', 'Bookshelves', 'My Review']
    
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=goodreads_columns)
        writer.writeheader()
        writer.writerows(flattened_data)


if __name__ == "__main__":
    json_file = "books_data.json"
    csv_file = "books_data.csv"
    convert_json_to_csv(json_file, csv_file)
    print(f"Data has been successfully converted to {csv_file}")