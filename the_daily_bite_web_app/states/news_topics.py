"""The News Topics application state."""

from typing import List, Optional

import pynecone as pc
from news_aggregator_data_access_layer.models.dynamodb import (
    NewsTopics,
    UserTopicSubscriptions,
    get_current_dt_utc_attribute,
)
from news_aggregator_data_access_layer.utils.telemetry import setup_logger

from the_daily_bite_web_app.config import GENERATE_DUMMY_DATA
from the_daily_bite_web_app.utils.aws_lambda import invoke_function

from .base import BaseState
from .models import NewsTopic

logger = setup_logger(__name__)


class NewsTopicsState(BaseState):
    """The news topics state."""

    news_topics: List[NewsTopic] = []
    is_loaded: bool = False
    is_refreshing_news_topics: bool = True
    is_updating_user_news_topic_subscriptions: bool = False

    def refreshing_news_topics(self):
        self.is_refreshing_news_topics = True

    def updating_news_topic_subscriptions(self):
        self.is_updating_user_news_topic_subscriptions = True

    def refresh_user_news_topics(self):
        """Get the news topics."""
        if self.user and self.user.user_id:
            logger.info(f"Value: {self.is_refreshing_news_topics}")
            self.refreshing_news_topics()
            logger.info(
                f"Refreshing news topics for user {self.user.user_id}. Value: {self.is_refreshing_news_topics}..."
            )
            # TODO - to test circular progress
            import time

            time.sleep(5)
            # TODO - can remove this
            if GENERATE_DUMMY_DATA:
                logger.info(f"GENERATE_DUMMY_DATA is set. Getting dummy data")
                self.news_topics = self.get_test_user_news_topics()
            else:
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
                            "category": news_topic.category,
                            "last_publishing_date": news_topic.last_publishing_date.isoformat()
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
            self.is_refreshing_news_topics = False
        else:
            logger.warning(f"User is not logged in. Cannot get news topics")

    def update_user_news_topic_subscriptions(self):
        """Update the user news topic subscriptions."""
        if self.user and self.user.user_id:
            self.updating_news_topic_subscriptions()
            # TODO - can remove this
            if GENERATE_DUMMY_DATA:
                logger.info(
                    f"GENERATE_DUMMY_DATA is set. Fake update user news topic subscriptions"
                )
                import time

                time.sleep(2)
            else:
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
                try:
                    for topic_id in news_topics_to_unsubscribe:
                        logger.info(
                            f"Unsubscribing user id {self.user.user_id} from topic id {topic_id}"
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
                        logger.info(
                            f"Subscribing user id {self.user.user_id} to topic id {topic_id}"
                        )
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
                except Exception as e:
                    logger.error(f"Error updating news topic subscriptions: {e}", exc_info=True)
                    self.is_updating_user_news_topic_subscriptions = False
                    # TODO - emit metric
                    self.refresh_user_news_topics()
                    return pc.window_alert(
                        "Error updating news topic subscriptions. Please try again."
                    )
            self.is_updating_user_news_topic_subscriptions = False
            self.refresh_user_news_topics()
            return pc.window_alert("News topics subscriptions updated successfully")
        else:
            logger.warning(f"User is not logged in. Cannot update news topic subscriptions")

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
        logger.info("Loading news topics...")
        self.refresh_user_news_topics()
        if self.is_loaded is False:
            pass
            # self.refresh_user_news_topics()
        #     self.refresh_user_news_topics()
        #     self.is_loaded = True
