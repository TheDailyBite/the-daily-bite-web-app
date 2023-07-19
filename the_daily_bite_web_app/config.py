import os

DEFAULT_LOGGER_NAME = "the-daily-bite-web-app"
DEFAULT_NAMESPACE = "the-daily-bite-web-app"
GENERATE_DUMMY_DATA = os.environ.get("GENERATE_DUMMY_DATA", "false").lower() in ["true"]
ARTICLES_PER_PAGE = int(os.environ.get("ARTICLES_PER_PAGE", 25))
DEFAULT_API_URL = "__API_URL__"
API_URL = os.environ.get("API_URL", DEFAULT_API_URL)
if "__" in API_URL:
    API_URL = "http://0.0.0.0:8000"
