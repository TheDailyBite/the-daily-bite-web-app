"""The News Topics application state."""

from typing import Dict, List, Optional

import pynecone as pc
from news_aggregator_data_access_layer.constants import SummarizationLength
from news_aggregator_data_access_layer.models.dynamodb import (
    SourcedArticles,
    get_current_dt_utc_attribute,
)
from news_aggregator_data_access_layer.utils.telemetry import setup_logger

from the_daily_bite_web_app.config import GENERATE_DUMMY_DATA

from .base import BaseState
from .models import ArticleSummarizationLength, NewsArticle, NewspaperTopic
from .news_topics import NewsTopicsState

logger = setup_logger(__name__)

DEFAULT_SUMMARIZATION_LENGTH = SummarizationLength.SHORT.value


class NewspaperState(NewsTopicsState):
    """The newspaper state."""

    newspaper: Dict[str, List[NewsArticle]] = dict()
    article_summarization_lengths: List[ArticleSummarizationLength] = [
        ArticleSummarizationLength(
            summarization_length=length.value,
            is_selected=False if length.value != DEFAULT_SUMMARIZATION_LENGTH else True,
        )
        for length in SummarizationLength
    ]
    newspaper_topics: List[NewspaperTopic] = []

    def article_summarization_length_selected(self, idx: int):
        """Set the selected article summarization length."""
        for i, article_summarization_length in enumerate(self.article_summarization_lengths):
            if i == idx:
                article_summarization_length.is_selected = True
            else:
                article_summarization_length.is_selected = False
        # NOTE - this is a temporary workaround to ensure the frontend receives the updated state
        self.article_summarization_lengths = self.article_summarization_lengths

    @pc.var
    def get_newspaper_topics(self) -> List[NewspaperTopic]:
        if not self.newspaper_topics:
            topics = [
                NewspaperTopic(
                    topic_id=topic.topic_id,
                    topic=topic.topic,
                    category=topic.category,
                    is_selected=True if idx == 0 else False,
                )
                for idx, topic in enumerate(self.get_user_subscribed_news_topics)
            ]
            self.newspaper_topics = topics
        return self.newspaper_topics

    @pc.var
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
        # TODO - probably need to add user id checks
        # TODO - issue - the user is not logged in when this is called
        self.refresh_user_news_topics()
        pass
