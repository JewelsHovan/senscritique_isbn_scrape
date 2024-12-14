"""
Configuration file for the isbn_scrape.py script.

This file contains all configurable parameters for the scraping process:
- Scraping behavior settings (workers, delay, batch size)
- Collection parameters (username, media type, sorting)
"""

# Scraping behavior settings
NUM_WORKERS = 3        # Number of concurrent workers
DELAY_TIME = 0.2      # Delay between requests in seconds
BATCH_SIZE = 18       # Number of items per request (default SC pagination)

# Collection parameters
USERNAME = "spif"     # Username whose collection to scrape
UNIVERSE = "book"     # Type of media to scrape: "book", "movie", "game", etc.
SORT_ORDER = "LAST_ACTION_DESC"  # How to sort the results

# Optional filters (set to None to disable)
CATEGORY_ID = None    # Filter by category
GENRE_ID = None      # Filter by genre
KEYWORDS = ""        # Search terms
YEAR_DONE = None     # Filter by completion year
YEAR_RELEASE = None  # Filter by release year