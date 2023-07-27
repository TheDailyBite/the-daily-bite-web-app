"""The News Topics application state."""

from typing import List, Optional

import asyncio

import reflex as rx
from news_aggregator_data_access_layer.models.dynamodb import (
    NewsTopics,
    NewsTopicSuggestions,
    UserTopicSubscriptions,
    get_current_dt_utc_attribute,
)
from news_aggregator_data_access_layer.utils.telemetry import setup_logger

from the_daily_bite_web_app.constants import NEWSPAPER_PATH
from the_daily_bite_web_app.utils.aws_lambda import invoke_function

from .base import BaseState
from .models import NewsTopic

logger = setup_logger(__name__)


class NewsTopicsState(BaseState):
    """The news topics state."""

    news_topics: List[NewsTopic] = []
    is_refreshing_news_topics: bool = True
    is_updating_user_news_topic_subscriptions: bool = False
    news_topic_suggestion: Optional[str] = ""

    def suggest_news_topic(self):
        if self.news_topic_suggestion:
            NewsTopicSuggestions(
                user_id=self.user.user_id,
                topic=self.news_topic_suggestion,
                created_at=get_current_dt_utc_attribute(),
            ).save()
            self.news_topic_suggestion = ""
            return rx.window_alert("Thank you for your suggestion!")

    def refresh_user_news_topics(self):
        """Get the news topics."""
        logger.info(f"Refreshing news topics for user...")
        if self.user and self.user.user_id:
            logger.info(f"Value: {self.is_refreshing_news_topics}")
            logger.info(
                f"Refreshing news topics for user {self.user.user_id}. Value: {self.is_refreshing_news_topics}..."
            )
            self.set_is_refreshing_news_topics(True)
            yield
            try:
                logger.info(f"Getting news topics for user {self.user.user_id}...")
                user_news_topics = UserTopicSubscriptions.query(self.user.user_id)
                user_news_topic_ids = [
                    user_news_topic.topic_id for user_news_topic in user_news_topics
                ]
                news_topics = NewsTopics.scan()
                published_news_topics = [
                    {
                        "topic_id": news_topic.topic_id,
                        "topic": news_topic.topic,
                        "last_publishing_date": news_topic.last_publishing_date.strftime(
                            "%Y-%m-%d %H:%M:%S"
                        )
                        if news_topic.last_publishing_date
                        else "",
                        "is_user_subscribed": news_topic.topic_id in user_news_topic_ids,
                    }
                    for news_topic in news_topics
                    if news_topic.is_published
                ]
                self.news_topics = [NewsTopic.parse_obj(r) for r in published_news_topics]
            except Exception as e:
                logger.error(f"Error getting news topics: {e}", exc_info=True)
                # TODO - emit metric
                self.news_topics = []
            self.set_is_refreshing_news_topics(False)
            yield
        else:
            logger.warning(f"User is not logged in. Cannot get news topics")

    def update_user_news_topic_subscriptions(self):
        """Update the user news topic subscriptions."""
        if self.user and self.user.user_id:
            self.set_is_updating_user_news_topic_subscriptions(True)
            yield
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
                yield
            try:
                for topic_id in news_topics_to_unsubscribe:
                    logger.info(
                        f"Unsubscribing user id {self.user.user_id} from topic id {topic_id}..."
                    )
                    try:
                        UserTopicSubscriptions(self.user.user_id, topic_id).delete()
                    except Exception as e:
                        logger.error(
                            f"Failed to unsubscribe user id {self.user.user_id} from topic id {topic_id} with error: {e}",
                            exc_info=True,
                        )
                        # TODO - emit metric
                        continue
                for topic_id in news_topics_to_subscribe:
                    logger.info(f"Subscribing user id {self.user.user_id} to topic id {topic_id}")
                    try:
                        UserTopicSubscriptions(
                            self.user.user_id,
                            topic_id,
                            date_subscribed=get_current_dt_utc_attribute(),
                        ).save()
                    except Exception as e:
                        logger.error(
                            f"Failed to subscribe user id {self.user.user_id} to topic id {topic_id} with error: {e}",
                            exc_info=True,
                        )
                        # TODO - emit metric
                        continue
                self.set_is_updating_user_news_topic_subscriptions(False)
                yield rx.redirect(NEWSPAPER_PATH)
            except Exception as e:
                logger.error(f"Error updating news topic subscriptions: {e}", exc_info=True)
                # TODO - emit metric
                yield rx.window_alert("Error updating news topic subscriptions. Please try again.")
        else:
            logger.warning(f"User is not logged in. Cannot update news topic subscriptions")

    def get_news_topic_ref(self, news_topic: NewsTopic) -> NewsTopic:
        """Get the news topic ref."""
        for news_topic_ref in self.news_topics:
            if news_topic_ref.topic_id == news_topic.topic_id:
                return news_topic_ref

    def toggle_news_topic_selected(self, news_topic: NewsTopic) -> None:
        """Toggle the selection of a news topic."""
        news_topic = NewsTopic.parse_obj(news_topic)
        news_topic_ref = self.get_news_topic_ref(news_topic)
        if news_topic_ref:
            news_topic_ref.is_selected = not news_topic_ref.is_selected
            # NOTE - this is a temporary workaround to ensure the frontend receives the updated state
            self.news_topics = self.news_topics

    @rx.var
    def get_user_subscribed_news_topics(self) -> List[NewsTopic]:
        """Get the user subscribed news topics."""
        return [news_topic for news_topic in self.news_topics if news_topic.is_user_subscribed]

    @rx.var
    def get_user_not_subscribed_news_topics(self) -> List[NewsTopic]:
        """Get the user not subscribed news topics."""
        return [news_topic for news_topic in self.news_topics if not news_topic.is_user_subscribed]

    def on_load(self):
        """Load the news topics."""
        logger.info("Loading news topics...")
        yield NewsTopicsState.refresh_user_news_topics()
