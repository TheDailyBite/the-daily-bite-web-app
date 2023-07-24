import os

DEFAULT_LOGGER_NAME = "the-daily-bite-web-app"
DEFAULT_NAMESPACE = "the-daily-bite-web-app"
GENERATE_DUMMY_DATA = os.environ.get("GENERATE_DUMMY_DATA", "false").lower() in ["true"]
ARTICLES_PER_PAGE = int(os.environ.get("ARTICLES_PER_PAGE", 5))
NEWSPAPER_REFRESH_FREQUENCY_MINS = int(os.environ.get("NEWSPAPER_REFRESH_FREQUENCY_MINS", 5))
MAX_SOURCES_PER_ARTICLE_IN_UI = int(os.environ.get("MAX_SOURCES_PER_ARTICLE_IN_UI", 10))
DEFAULT_API_URL = "__API_URL__"
API_URL = os.environ.get("API_URL", DEFAULT_API_URL)
if "__" in API_URL:
    API_URL = "http://0.0.0.0:8000"
