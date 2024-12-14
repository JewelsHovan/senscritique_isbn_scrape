"""
Enhanced book scraper using GraphQL API for collection data and asynchronous requests for details.

This script performs the following actions:
1. Fetches a list of books from a user's collection on SensCritique using the GraphQL API.
2. Scrapes detailed information for each book by making asynchronous requests to their individual pages.
3. Saves the collected book data into a JSON file.

The script is designed to be efficient by using asynchronous programming to handle multiple requests concurrently,
and it provides progress updates using tqdm.
"""

import json
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from dataclasses import dataclass
from tqdm.asyncio import tqdm
from config import (
    NUM_WORKERS, DELAY_TIME, BATCH_SIZE, USERNAME, 
    UNIVERSE, SORT_ORDER, CATEGORY_ID, GENRE_ID, 
    KEYWORDS, YEAR_DONE, YEAR_RELEASE
)
@dataclass
class GraphQLConfig:
    """
    Configuration for GraphQL requests.

    Attributes:
        URL (str): The URL endpoint for the GraphQL API.
        HEADERS (Dict[str, str]): Headers to be used in the GraphQL requests.
        QUERY (str): The GraphQL query to fetch user collection data.
    """
    URL: str = "https://apollo.senscritique.com/"
    HEADERS: Dict[str, str] = None
    QUERY: str = """
    query UserCollection($action: ProductAction, $categoryId: Int, $gameSystemId: Int, 
                        $genreId: Int, $isAgenda: Boolean, $keywords: String, $limit: Int, 
                        $month: Int, $offset: Int, $order: CollectionSort, $showTvAgenda: Boolean, 
                        $universe: String, $username: String!, $versus: Boolean, $year: Int, 
                        $yearDateDone: Int, $yearDateRelease: Int) {
        user(username: $username) {
            collection(
                action: $action
                categoryId: $categoryId
                gameSystemId: $gameSystemId
                genreId: $genreId
                isAgenda: $isAgenda
                keywords: $keywords
                limit: $limit
                month: $month
                offset: $offset
                order: $order
                showTvAgenda: $showTvAgenda
                universe: $universe
                versus: $versus
                year: $year
                yearDateDone: $yearDateDone
                yearDateRelease: $yearDateRelease
            ) {
                total
                products {
                    title
                    id
                    url
                    yearOfProduction
                    __typename
                }
                __typename
            }
        }
    }
    """

async def fetch_collection_data(session: aiohttp.ClientSession, 
                              config: GraphQLConfig, 
                              variables: Dict[str, Any]) -> Dict:
    """
    Fetches collection data using the GraphQL API.

    Args:
        session (aiohttp.ClientSession): The aiohttp client session.
        config (GraphQLConfig): Configuration for the GraphQL request.
        variables (Dict[str, Any]): Variables to be used in the GraphQL query.

    Returns:
        Dict: The JSON response from the GraphQL API.

    Raises:
        aiohttp.ClientResponseError: If the response status is not ok.
    """
    payload = {
        "operationName": "UserCollection",
        "variables": variables,
        "query": config.QUERY
    }
    
    async with session.post(config.URL, 
                          headers=config.HEADERS, 
                          json=payload) as response:
        response.raise_for_status()
        return await response.json()

async def collect_all_books(session: aiohttp.ClientSession, 
                          config: GraphQLConfig) -> List[Dict]:
    """
    Collects all books from the collection using pagination.

    Args:
        session (aiohttp.ClientSession): The aiohttp client session.
        config (GraphQLConfig): Configuration for the GraphQL request.

    Returns:
        List[Dict]: A list of dictionaries, each representing a book.
    """
    all_results = []
    offset = 0
    limit = BATCH_SIZE
    
    variables = {
        "action": None,
        "categoryId": CATEGORY_ID,
        "gameSystemId": None,
        "genreId": GENRE_ID,
        "keywords": KEYWORDS,
        "limit": limit,
        "offset": 0,
        "order": SORT_ORDER,
        "universe": UNIVERSE,
        "username": USERNAME,
        "yearDateDone": YEAR_DONE,
        "yearDateRelease": YEAR_RELEASE
    }

    with tqdm(desc="Collecting book URLs") as pbar:
        while True:
            variables["offset"] = offset
            try:
                data = await fetch_collection_data(session, config, variables)
                products = data.get("data", {}).get("user", {}).get("collection", {}).get("products", [])
                
                if not products:
                    break
                    
                all_results.extend(products)
                offset += limit
                pbar.update(len(products))
                
            except Exception as e:
                print(f"Error fetching offset {offset}: {e}")
                break
    
    return all_results

async def scrape_book_details(session: aiohttp.ClientSession, 
                            book: Dict, 
                            semaphore: asyncio.Semaphore) -> Dict:
    """
    Scrapes detailed information for a single book.

    Args:
        session (aiohttp.ClientSession): The aiohttp client session.
        book (Dict): A dictionary representing a book with at least a 'url' key.
        semaphore (asyncio.Semaphore): Semaphore to limit concurrent requests.

    Returns:
        Dict: A dictionary containing detailed information about the book, or None if an error occurs.
    """
    async with semaphore:
        try:

            await asyncio.sleep(DELAY_TIME)
            async with session.get(f"https://www.senscritique.com{book['url']}") as response:
                content = await response.text()
                soup = BeautifulSoup(content, 'html.parser')
                
                ld_json = soup.find('script', {'type': 'application/ld+json'})
                if ld_json:
                    book_data = json.loads(ld_json.string)
                    return {
                        'id': book['id'],
                        'title': book_data.get('name'),
                        'author': [creator['name'] for creator in book_data.get('creator', [])],
                        'isbn': book_data.get('isbn'),
                        'description': book_data.get('description'),
                        'genres': book_data.get('genre', []),
                        'rating': book_data.get('aggregateRating', {}).get('ratingValue'),
                        'rating_count': book_data.get('aggregateRating', {}).get('ratingCount'),
                        'image_url': book_data.get('image'),
                        'publication_date': book_data.get('dateCreated'),
                        'year_of_production': book['yearOfProduction']
                    }
        except Exception as e:
            print(f"Error scraping book {book['url']}: {e}")
            return None

async def main():
    """
    Main execution function.

    This function orchestrates the scraping process:
    1. Collects all book URLs from the user's collection.
    2. Scrapes details for each book concurrently.
    3. Saves the results to a JSON file.
    """
    config = GraphQLConfig()
    config.HEADERS = {
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'content-type': 'application/json',
        'origin': 'https://www.senscritique.com',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    async with aiohttp.ClientSession() as session:
        # Collect all book URLs
        books = await collect_all_books(session, config)
        print(f"\nFound {len(books)} books")

        # Scrape details for each book
        semaphore = asyncio.Semaphore(NUM_WORKERS)  # Limit concurrent requests
        tasks = [
            scrape_book_details(session, book, semaphore)
            for book in books
        ]
        
        results = await tqdm.gather(*tasks, desc="Scraping book details")
        # Filter out None results (failed scrapes)
        valid_results = [r for r in results if r is not None]

        # Save results
        print(f"\nSuccessfully scraped {len(valid_results)} books")
        with open('books_data.json', 'w', encoding='utf-8') as f:
            json.dump(valid_results, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    asyncio.run(main())
