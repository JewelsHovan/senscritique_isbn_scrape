# SensCritique Book Scraper

An asynchronous Python script that efficiently scrapes book data from SensCritique collections and saves it to a JSON file. The script uses concurrent workers to collect comprehensive book details including titles, authors, ISBNs, descriptions, genres, ratings, and more.

## Features

- Asynchronous scraping using aiohttp for improved performance
- Concurrent processing with 3 workers and rate limiting
- Scrapes multiple pages of book collections from SensCritique
- Extracts detailed book information including:
  - Title
  - Author(s)
  - ISBN
  - Description
  - Genres
  - Rating and rating count
  - Cover image URL
  - Publication date
- Saves data in a structured JSON format
- Implements respectful scraping with 0.2s delay between requests
- Uses proper User-Agent headers

## Requirements

```python
python
aiohttp
beautifulsoup4
asyncio
```

## Usage

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the script:
   ```bash
   python isbn_scrape.py
   ```

The script will create a `books_data.json` file containing all scraped book information.

## Configuration

The script uses these default settings:
- Base URL: `https://www.senscritique.com/spif/collection?universe=2`
- Concurrent workers: 3
- Request delay: 0.2 seconds
- These settings can be adjusted in the config.py file

## To Do

- [x] Make page range dynamic instead of hardcoded
- [x] Implement asynchronous requests for ISBN data collection to improve performance
- [x] Implement concurrent workers with rate limiting
- [ ] Add a progress bar for better user feedback
- [ ] Add error handling and retry mechanisms
- [ ] Implement command-line arguments for configuration
- [ ] Add data validation
- [ ] Create proper logging system

## Legal Notice

Please ensure you comply with SensCritique's terms of service and robots.txt when using this scraper. The script implements appropriate delays and rate limiting between requests to avoid overwhelming their servers.

## Performance Note

The asynchronous implementation with 3 concurrent workers significantly improves scraping performance while maintaining respectful request rates. The 0.2-second delay between requests ensures the script doesn't overwhelm the server.