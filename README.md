# SensCritique Book Scraper

A Python script that scrapes book data from collection on SensCritique and saves it to a JSON file. The script collects comprehensive book details including titles, authors, ISBNs, descriptions, genres, ratings, and more.

## Features

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
- Implements respectful scraping with delay between requests
- Uses proper User-Agent headers

## Requirements

```python
requests
beautifulsoup4
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

Currently, the script uses these default settings:
- Base URL: `https://www.senscritique.com/spif/collection?universe=2` (check this to point to a different collection url)
- Request delay: 0.2 seconds

## To Do

- [x] Make page range dynamic instead of hardcoded
- [ ] Implement asynchronous requests for ISBN data collection to improve performance
- [ ] Add a progress bar for better user feedback
- [ ] Add error handling and retry mechanisms
- [ ] Implement command-line arguments for configuration
- [ ] Add data validation
- [ ] Create proper logging system

## Legal Notice

Please ensure you comply with SensCritique's terms of service and robots.txt when using this scraper. Implement appropriate delays between requests to avoid overwhelming their servers.
