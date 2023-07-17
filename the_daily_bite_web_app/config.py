import os

DEFAULT_LOGGER_NAME = "the-daily-bite-web-app"
DEFAULT_NAMESPACE = "the-daily-bite-web-app"
GENERATE_DUMMY_DATA = os.environ.get("GENERATE_DUMMY_DATA", "false").lower() in ["true"]
ARTICLES_PER_PAGE = int(os.environ.get("ARTICLES_PER_PAGE", 25))
BACKEND_PORT = os.environ.get("BACKEND_PORT", "8000")
DEFAULT_BACKEND_HOST = "__BACKEND_HOST__"
BACKEND_HOST = os.environ.get("BACKEND_HOST", DEFAULT_BACKEND_HOST)
if BACKEND_HOST == DEFAULT_BACKEND_HOST:
    BACKEND_HOST = "http://0.0.0.0"
