import os

DEFAULT_LOGGER_NAME = "the-daily-bite-web-app"
DEFAULT_NAMESPACE = "the-daily-bite-web-app"
GENERATE_DUMMY_DATA = os.environ.get("GENERATE_DUMMY_DATA", "true").lower() in ["true"]