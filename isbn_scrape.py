"""
This module scrapes book data from SensCritique and saves it to a JSON file.

It uses the requests library to fetch web pages and BeautifulSoup to parse the HTML content.
The script iterates through multiple pages of a collection on SensCritique, extracts book URLs,
and then scrapes details from each book's page. The extracted data includes title, author, ISBN,
description, genres, rating, rating count, image URL, and publication date. Finally, it saves
the collected data into a JSON file named 'books_data.json'.
"""

import requests
from bs4 import BeautifulSoup
import time
import json


def get_num_pages(base_url, headers):
    """
    Retrieves the total number of pages in a SensCritique collection.

    Args:
        base_url (str): The base URL of the collection.
        headers (dict): HTTP headers to use in the request.

    Returns:
        int: The total number of pages, or None if an error occurs.
    """
    response = requests.get(base_url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    nav = soup.find('nav', {'aria-label': 'Navigation de la pagination'})
    if nav:
        last_span = nav.find_all('span')[-1] # Get the last span in the list
        number_str = last_span.text
        try:
            number = int(number_str)
            return number
        except ValueError:
            print("Could not convert to integer")
    return None

def scrape_book_urls(base_url, page_end, headers):
    """
    Scrapes book URLs from multiple pages of a SensCritique collection.

    Args:
        base_url (str): The base URL of the collection.
        page_end (int): The last page number to scrape.
        headers (dict): HTTP headers to use in requests.

    Returns:
        list: A list of book URLs.
    """
    all_book_urls = []
    page_number = 1
    while page_number <= page_end:
        url = f"{base_url}?page={page_number}" # this is how we will navigate through the pages
        response = requests.get(url, headers=headers)
        time.sleep(0.2)  # Respectful delay between requests
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            book_elements = soup.find_all('div', {'data-testid': 'product-list-item'})

            if not book_elements:  # No more books found, exit loop
                break

            # we iterate through the book elements and extract the book url
            for book_element in book_elements:
                title_element = book_element.find('a', {'data-testid': 'product-title'})
                if title_element:
                    # we construct the book url by adding the href to the base url
                    book_url = "https://www.senscritique.com" + title_element['href']
                    all_book_urls.append(book_url)

            page_number += 1
        else:
            print(f"Error fetching page {page_number}: Status code {response.status_code}")
            break

    print(f"Scraped {len(all_book_urls)} book URLs")
    return all_book_urls

def scrape_book_details(book_url, headers):
    """
    Scrapes details of a single book from its SensCritique page.

    Args:
        book_url (str): The URL of the book's page.
        headers (dict): HTTP headers to use in requests.

    Returns:
        dict: A dictionary containing book details.
    """
    response = requests.get(book_url, headers=headers)
    time.sleep(0.2)  # Respectful delay between requests
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        ld_application_schema = soup.find('script', {'type': 'application/ld+json'})
        
        if ld_application_schema:
            book_data = json.loads(ld_application_schema.string)
            book_details = {
                'title': book_data.get('name'),
                'author': [creator['name'] for creator in book_data.get('creator', [])],
                'isbn': book_data.get('isbn'),
                'description': book_data.get('description'),
                'genres': book_data.get('genre', []),
                'rating': book_data.get('aggregateRating', {}).get('ratingValue'),
                'rating_count': book_data.get('aggregateRating', {}).get('ratingCount'),
                'image_url': book_data.get('image'),
                'publication_date': book_data.get('dateCreated')
            }
            return book_details
    return None


if __name__ == "__main__":
    # Define headers with a common browser User-Agent (this bypassses the bot detection)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36'
    }

    # CHANGE THESE VALUES TO CHANGE THE COLLECTION SCRAPED
    base_url = "https://www.senscritique.com/spif/collection?universe=2"

    num_pages = get_num_pages(base_url, headers)
    print(f"Number of pages: {num_pages}")

    # Scrape book URLs
    print("Scraping book URLs...")
    all_book_urls = scrape_book_urls(base_url, num_pages, headers)

    # Scrape details for each book (this could be sped up with async requests)
    print("Scraping individual book details...")
    all_books = []
    for i, book_url in enumerate(all_book_urls):
        book_details = scrape_book_details(book_url, headers)
        if book_details:
            all_books.append(book_details)
            print(f"Processed book {i+1} of {len(all_book_urls)}", end='\r')

    # Save to JSON file with proper formatting and UTF-8 encoding
    with open('books_data.json', 'w', encoding='utf-8') as f:
        json.dump(all_books, f, ensure_ascii=False, indent=4)

    print(f"Saved {len(all_books)} books to books_data.json")
