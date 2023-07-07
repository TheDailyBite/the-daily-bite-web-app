"""The News Topics application state."""

from typing import Dict, List, Optional

import reflex as rx
from news_aggregator_data_access_layer.constants import SummarizationLength
from news_aggregator_data_access_layer.models.dynamodb import (
    SourcedArticles,
    NewsTopics,
    UserTopicSubscriptions,    
)
from news_aggregator_data_access_layer.utils.telemetry import setup_logger

from the_daily_bite_web_app.config import GENERATE_DUMMY_DATA

from .base import BaseState
from .models import ArticleSummarizationLength, NewsArticle, NewspaperTopic

logger = setup_logger(__name__)

DEFAULT_SUMMARIZATION_LENGTH = SummarizationLength.SHORT.value


class NewspaperState(BaseState):
    """The newspaper state."""

    # newspaper: Dict[str, List[NewsArticle]] = dict()
    article_summarization_lengths: List[ArticleSummarizationLength] = [
        ArticleSummarizationLength(
            summarization_length=length.value,
            is_selected=False if length.value != DEFAULT_SUMMARIZATION_LENGTH else True,
        )
        for length in SummarizationLength
    ]
    newspaper_topics: List[NewspaperTopic] = []
    is_refreshing_news_topics: bool = True

    def refreshing_news_topics(self) -> None:
        self.is_refreshing_news_topics = True

    def refresh_user_subscribed_newspaper_topics(self):
        # """Get the news topics."""
        logger.info(f"Refreshing subscribed newspaper topics for user...")
        if self.user and self.user.user_id:
            logger.info(f"User Name: {self.user.name};")
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
                self.newspaper_topics = self.get_test_user_newspaper_topics()
            else:
                try:
                    logger.info(f"Getting newspaper topics for user {self.user.user_id}...")
                    user_news_topics = UserTopicSubscriptions.query(self.user.user_id)
                    user_news_topic_ids = [
                        (user_news_topic.topic_id) for user_news_topic in user_news_topics
                    ]
                    news_topics = NewsTopics.batch_get(user_news_topic_ids)
                    subscribed_newspaper_topics = [
                        {
                            "topic_id": news_topic.topic_id,
                            "topic": news_topic.topic,
                            "category": news_topic.category,
                            "is_selected": True if idx == 0 else False,
                        }
                        for idx, news_topic in enumerate(news_topics)
                        if news_topic.is_published
                    ]
                    self.newspaper_topics = [
                        NewspaperTopic.parse_obj(r) for r in subscribed_newspaper_topics
                    ]
                except Exception as e:
                    logger.error(f"Error getting news topics: {e}", exc_info=True)
                    # TODO - emit metric
                    self.newspaper_topics = []
            self.is_refreshing_news_topics = False
        else:
            logger.warning(f"User is not logged in. Cannot get news topics")

    # TODO - remove
    def get_test_user_newspaper_topics(self) -> List[NewspaperTopic]:
        return [
            NewspaperTopic(
                topic_id="1",
                topic="Topic 1",
                category="Category 1",
                is_selected=True,
            ),
            NewspaperTopic(
                topic_id="2",
                topic="Topic 2",
                category="Category 2",
                is_selected=False,
            ),
            NewspaperTopic(
                topic_id="3",
                topic="Topic 3",
                category="Category 3",
                is_selected=False,
            ),
        ]

    def article_summarization_length_selected(self, idx: int):
        """Set the selected article summarization length."""
        for i, article_summarization_length in enumerate(self.article_summarization_lengths):
            if i == idx:
                article_summarization_length.is_selected = True
            else:
                article_summarization_length.is_selected = False
        # NOTE - this is a temporary workaround to ensure the frontend receives the updated state
        self.article_summarization_lengths = self.article_summarization_lengths

    @rx.var
    def get_newspaper_topics(self) -> List[NewspaperTopic]:
        return [topic for topic in self.newspaper_topics]

    def newspaper_topic_selected(self, idx: int):
        """Set the selected newspaper topic."""
        for i, newspaper_topic in enumerate(self.newspaper_topics):
            if i == idx:
                newspaper_topic.is_selected = True
            else:
                newspaper_topic.is_selected = False
        # NOTE - this is a temporary workaround to ensure the frontend receives the updated state
        self.newspaper_topics = self.newspaper_topics

    @rx.var
    def get_selected_article_summarization_length(self) -> ArticleSummarizationLength:
        """Get the selected article summarization length."""
        selected_article_summarization_length = None
        for article_summarization_length in self.article_summarization_lengths:
            if article_summarization_length.is_selected:
                selected_article_summarization_length = article_summarization_length
                return selected_article_summarization_length

    def on_load_newspaper(self):
        """Load the news topics."""
        logger.info(f"Loading newspaper state...")
        self.refresh_user_subscribed_newspaper_topics()
