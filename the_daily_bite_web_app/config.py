import os

# login
NEWS_SERVICE_LOGIN_URL = os.environ.get("NEWS_SERVICE_LOGIN_URL")
USER_LOGIN_FUNCTION_NAME = os.environ.get("USER_LOGIN_FUNCTION_NAME")
# get news topics
NEWS_SERVICE_GET_NEWS_TOPICS_URL = os.environ.get("NEWS_SERVICE_GET_NEWS_TOPICS_URL")
GET_NEWS_TOPICS_FUNCTION_NAME = os.environ.get("GET_NEWS_TOPICS_FUNCTION_NAME")
# subscribe news topics
NEWS_SERVICE_SUBSCRIBE_NEWS_TOPICS_URL = os.environ.get("NEWS_SERVICE_SUBSCRIBE_NEWS_TOPICS_URL")
SUBSCRIBE_NEWS_TOPICS_FUNCTION_NAME = os.environ.get("SUBSCRIBE_NEWS_TOPICS_FUNCTION_NAME")

REGION_NAME = os.environ.get("REGION_NAME", "us-west-1")
LOCAL_TESTING = os.environ.get("LOCAL_TESTING", "false").lower() in ["true"]
DEFAULT_LOGGER_NAME = "the-daily-bite-web-app"
DEFAULT_NAMESPACE = "the-daily-bite-web-app"
