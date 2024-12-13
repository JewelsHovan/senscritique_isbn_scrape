"""
This module asynchronously scrapes book data from SensCritique and saves it to a JSON file.

It utilizes aiohttp for asynchronous HTTP requests and BeautifulSoup for parsing HTML content.
The script implements concurrent scraping with rate limiting to respectfully fetch data from 
SensCritique's website. It iterates through multiple pages of a collection, extracts book URLs,
and then concurrently scrapes details from each book's page. The extracted data includes:

- Title
- Author(s)
- ISBN
- Description
- Genres
- Rating
- Rating count
- Image URL
- Publication date

The collected data is saved into a JSON file named 'books_data.json'.
"""

from bs4 import BeautifulSoup
import json
import aiohttp
import asyncio
from asyncio import Semaphore
from config import BASE_URL, NUM_WORKERS, DELAY_TIME

async def get_num_pages(base_url, headers, session):
    """
    Asynchronously fetches the total number of pages in the book collection.

    Args:
        base_url (str): The base URL of the SensCritique collection.
        headers (dict): HTTP headers for the request.
        session (aiohttp.ClientSession): The aiohttp client session.

    Returns:
        int or None: The total number of pages, or None if an error occurs.
    """
    async with session.get(base_url, headers=headers) as response:
        content = await response.text()
        soup = BeautifulSoup(content, 'html.parser')
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

async def scrape_book_urls(base_url, page_end, headers, session, semaphore):
    """
    Asynchronously scrapes book URLs from multiple pages of a SensCritique collection.

    Args:
        base_url (str): The base URL of the collection.
        page_end (int): The last page number to scrape.
        headers (dict): HTTP headers for the requests.
        session (aiohttp.ClientSession): The aiohttp client session.
        semaphore (asyncio.Semaphore): Semaphore to limit concurrent requests.

    Returns:
        list: A list of URLs pointing to individual book pages.
    """
    all_book_urls = []
    page_number = 1
    
    while page_number <= page_end:
        async with semaphore:  # Limit concurrent requests
            await asyncio.sleep(0.2)  # Respectful delay
            url = f"{base_url}?page={page_number}"
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    content = await response.text()
                    soup = BeautifulSoup(content, 'html.parser')
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
                else:
                    print(f"Error fetching page {page_number}: Status code {response.status}")
                    break
        page_number += 1
    
    return all_book_urls

async def scrape_book_details(book_url, headers, session, semaphore):
    """
    Asynchronously scrapes details of a single book from its SensCritique page.

    Args:
        book_url (str): The URL of the book's page.
        headers (dict): HTTP headers for the request.
        session (aiohttp.ClientSession): The aiohttp client session.
        semaphore (asyncio.Semaphore): Semaphore to limit concurrent requests.

    Returns:
        dict or None: A dictionary containing book details, or None if an error occurs.
    """
    async with semaphore:  # Limit concurrent requests
        await asyncio.sleep(DELAY_TIME)  # Respectful delay
        async with session.get(book_url, headers=headers) as response:
            if response.status == 200:
                content = await response.text()
                soup = BeautifulSoup(content, 'html.parser')
                # normally I like using extruct's LDJsonExtractor but to keep it simple 
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

async def main():
    """
    Main asynchronous function to orchestrate the scraping process.
    
    This function initializes the aiohttp session, determines the number of pages to scrape,
    fetches book URLs, concurrently scrapes book details, and saves the data to a JSON file.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36'
    }
    base_url = BASE_URL
    
    # Create semaphore for concurrent workers
    semaphore = Semaphore(NUM_WORKERS)  # Limit to NUM_WORKERS concurrent requests
    
    async with aiohttp.ClientSession() as session:
        # Get number of pages
        num_pages = await get_num_pages(base_url, headers, session)
        print(f"Number of pages: {num_pages}")
        
        # Scrape book URLs
        print("Scraping book URLs...")
        all_book_urls = await scrape_book_urls(base_url, num_pages, headers, session, semaphore)
        
        # Scrape book details concurrently
        print("Scraping individual book details...")
        tasks = []
        for book_url in all_book_urls:
            task = asyncio.create_task(scrape_book_details(book_url, headers, session, semaphore))
            tasks.append(task)
        
        all_books = []
        for i, task in enumerate(asyncio.as_completed(tasks)):
            book_details = await task
            if book_details:
                all_books.append(book_details)
                print(f"Processed book {i+1} of {len(all_book_urls)}", end='\r')
    
    # Save to JSON file
    with open('books_data.json', 'w', encoding='utf-8') as f:
        json.dump(all_books, f, ensure_ascii=False, indent=4)
    
    print(f"\nSaved {len(all_books)} books to books_data.json")

if __name__ == "__main__":
    asyncio.run(main())
