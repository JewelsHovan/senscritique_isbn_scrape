# SensCritique Collection Scraper

An asynchronous Python script that efficiently scrapes collection data from SensCritique and saves it to JSON and CSV formats. The script uses concurrent workers to collect comprehensive details including titles, authors, ISBNs, descriptions, genres, ratings, and more.

## Features

- Asynchronous scraping using aiohttp for improved performance
- Concurrent processing with configurable workers and rate limiting
- Scrapes multiple pages of collections from SensCritique
- Extracts detailed information including:
  - Title
  - Author(s)
  - ISBN
  - Description
  - Genres
  - Rating and rating count
  - Cover image URL
  - Publication date
- Saves data in both JSON and CSV formats (CSV format compatible with Goodreads import)
- Implements respectful scraping with configurable delays between requests
- Uses proper User-Agent headers

## Requirements

```bash
python 3.7+
aiohttp
beautifulsoup4
asyncio
tqdm
```

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

Edit `config.py` to customize the scraping behavior:

```python
# Scraping behavior settings
NUM_WORKERS = 3        # Number of concurrent workers
DELAY_TIME = 0.2      # Delay between requests in seconds
BATCH_SIZE = 18       # Number of items per request

# Collection parameters
USERNAME = "spif"     # Username whose collection to scrape
UNIVERSE = "book"     # Type of media: "book", "movie", "game", etc.
SORT_ORDER = "LAST_ACTION_DESC"  # How to sort the results

# Optional filters (set to None to disable)
CATEGORY_ID = None    # Filter by category
GENRE_ID = None      # Filter by genre
KEYWORDS = ""        # Search terms
YEAR_DONE = None     # Filter by completion year
YEAR_RELEASE = None  # Filter by release year
```

## Usage

1. Update the configuration in `config.py` with your desired settings (especially the USERNAME)

2. Run the scraper:
   ```bash
   python isbn_scrape.py
   ```
   This will create a `books_data.json` file containing all scraped information.

3. (Optional) Convert the JSON data to CSV format:
   ```bash
   python convert_to_csv.py
   ```
   This will create a `books_data.csv` file in Goodreads-compatible format.

## Output Files

- `books_data.json`: Raw scraped data in JSON format
- `books_data.csv`: Converted data in Goodreads-compatible CSV format

## Performance Notes

- The asynchronous implementation with configurable concurrent workers improves scraping performance
- Default settings (3 workers, 0.2s delay) provide a good balance between speed and server respect
- Adjust NUM_WORKERS and DELAY_TIME in config.py based on your needs and server limitations

## Legal Notice

Please ensure you comply with SensCritique's terms of service and robots.txt when using this scraper. The script implements appropriate delays and rate limiting between requests to avoid overwhelming their servers.

## To Do

- [x] Make page range dynamic instead of hardcoded
- [x] Implement asynchronous requests
- [x] Implement concurrent workers with rate limiting
- [x] Add a progress bar for better user feedback
- [x] Add CSV export functionality
- [ ] Add error handling and retry mechanisms
- [ ] Implement command-line arguments for configuration
- [ ] Add data validation
- [ ] Create proper logging system

## Troubleshooting

If you encounter issues:
1. Verify your internet connection
2. Check if the username in config.py is correct
3. Try increasing DELAY_TIME if you're getting rate limited
4. Ensure you have the correct Python version and all dependencies installed
