import os
CACHE_TTL = int(os.getenv("CACHE_TTL", 60))  # Cache time-to-live in seconds
REDIS_URL = os.getenv("REDIS_URL", "")  # Redis connection URL
USER_AGENT = os.getenv("USER_AGENT", "price-aggregator-mvp/1.0")  # Default User-Agent header
MAX_SCRAPE_RESULTS = int(os.getenv("MAX_SCRAPE_RESULTS", 30))  # Max number of scrape results to
