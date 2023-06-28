"""The News Topics application state."""

from typing import List, Optional

import pynecone as pc

from the_daily_bite_web_app.config import (
    GET_NEWS_TOPICS_FUNCTION_NAME,
    NEWS_SERVICE_GET_NEWS_TOPICS_URL,
    NEWS_SERVICE_SUBSCRIBE_NEWS_TOPICS_URL,
    SUBSCRIBE_NEWS_TOPICS_FUNCTION_NAME,
)
from the_daily_bite_web_app.utils.aws_lambda import invoke_function

from .base import BaseState
from .models import NewsTopic


class NewsTopicsState(BaseState):
    """The news topics state."""

    news_topics: List[NewsTopic] = []
    is_loaded: bool = False

    def refresh_user_news_topics(self):
        """Get the news topics."""
        if self.user and self.user.user_id:
            # TODO - can remove this
            if not GET_NEWS_TOPICS_FUNCTION_NAME and not NEWS_SERVICE_GET_NEWS_TOPICS_URL:
                print(
                    f"GET_NEWS_TOPICS_FUNCTION_NAME and NEWS_SERVICE_GET_NEWS_TOPICS_URL are not set. Getting dummy data"
                )
                self.news_topics = self.get_test_user_news_topics()
                return
            response = invoke_function(
                GET_NEWS_TOPICS_FUNCTION_NAME,
                {"user_id": self.user.user_id},
                function_url=NEWS_SERVICE_GET_NEWS_TOPICS_URL,
            )
            if response["statusCode"] == 200:
                body = response["body"]
                self.news_topics = [NewsTopic.parse_obj(r) for r in body["results"]]

    def update_user_news_topic_subscriptions(self):
        """Update the user news topic subscriptions."""
        if self.user and self.user.user_id:
            news_topics_to_unsubscribe = [
                news_topic.topic_id
                for news_topic in self.news_topics
                if news_topic.is_user_subscribed and news_topic.is_selected
            ]
            news_topics_to_subscribe = [
                news_topic.topic_id
                for news_topic in self.news_topics
                if not news_topic.is_user_subscribed and news_topic.is_selected
            ]
            if not news_topics_to_unsubscribe and not news_topics_to_subscribe:
                return
            # TODO - can remove this
            if (
                not SUBSCRIBE_NEWS_TOPICS_FUNCTION_NAME
                and not NEWS_SERVICE_SUBSCRIBE_NEWS_TOPICS_URL
            ):
                print(
                    f"SUBSCRIBE_NEWS_TOPICS_FUNCTION_NAME and NEWS_SERVICE_SUBSCRIBE_NEWS_TOPICS_URL are not set. Not subscribing. Unsubscribe values: {news_topics_to_unsubscribe}; Subscribe values: {news_topics_to_subscribe}"
                )
                return
            response = invoke_function(
                SUBSCRIBE_NEWS_TOPICS_FUNCTION_NAME,
                {
                    "user_id": self.user.user_id,
                    "news_topics_to_unsubscribe": news_topics_to_unsubscribe,
                    "news_topics_to_subscribe": news_topics_to_subscribe,
                },
                function_url=NEWS_SERVICE_SUBSCRIBE_NEWS_TOPICS_URL,
            )
            self.refresh_user_news_topics()
            return pc.window_alert("News topics subscriptions updated successfully")

    # TODO - remove
    def get_test_user_news_topics(self) -> List[NewsTopic]:
        return [
            NewsTopic(
                topic_id="1",
                topic="Topic 1",
                category="Category 1",
                last_publishing_date="2021-01-01",
                is_user_subscribed=True,
            ),
            NewsTopic(
                topic_id="2",
                topic="Topic 2",
                category="Category 2",
                last_publishing_date="2021-01-02",
                is_user_subscribed=False,
            ),
            NewsTopic(
                topic_id="3",
                topic="Topic 3",
                category="Category 3",
                last_publishing_date="2021-01-03",
                is_user_subscribed=True,
            ),
        ]

    def toggle_news_topic_selected(self, news_topic_idx: int) -> None:
        """Toggle the selection of a news topic."""
        news_topic = self.news_topics[news_topic_idx]
        news_topic.is_selected = not news_topic.is_selected
        # NOTE - this is a temporary workaround to ensure the frontend receives the updated state
        self.news_topics = self.news_topics

    @pc.var
    def get_user_subscribed_news_topics(self) -> List[NewsTopic]:
        """Get the user subscribed news topics."""
        return [news_topic for news_topic in self.news_topics if news_topic.is_user_subscribed]

    @pc.var
    def get_user_not_subscribed_news_topics(self) -> List[NewsTopic]:
        """Get the user not subscribed news topics."""
        return [news_topic for news_topic in self.news_topics if not news_topic.is_user_subscribed]

    def on_load(self):
        """Load the news topics."""
        if self.is_loaded is False:
            # self.refresh_user_news_topics_test()
            self.refresh_user_news_topics()
            self.is_loaded = True
