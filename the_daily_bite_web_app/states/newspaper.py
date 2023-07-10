"""The News Topics application state."""

from typing import Dict, List, Optional, Tuple, Union

import reflex as rx
from news_aggregator_data_access_layer.config import SOURCED_ARTICLES_S3_BUCKET
from news_aggregator_data_access_layer.constants import SummarizationLength
from news_aggregator_data_access_layer.models.dynamodb import (
    NewsTopics,
    SourcedArticles,
    UserTopicSubscriptions,
)
from news_aggregator_data_access_layer.utils.s3 import (
    get_object,
    lexicographic_date_s3_prefix_to_dt,
)
from news_aggregator_data_access_layer.utils.telemetry import setup_logger

from the_daily_bite_web_app.config import ARTICLES_PER_PAGE, GENERATE_DUMMY_DATA

from .base import BaseState
from .models import ArticleSummarizationLength, NewsArticle, NewspaperTopic

logger = setup_logger(__name__)

DEFAULT_SUMMARIZATION_LENGTH = SummarizationLength.SHORT.value


class NewspaperState(BaseState):
    """The newspaper state."""

    # will be topic id: published date: list of articles
    newspaper: Dict[str, Dict[str, List[NewsArticle]]] = dict()
    article_summarization_lengths: List[ArticleSummarizationLength] = [
        ArticleSummarizationLength(
            summarization_length=length.value,
            is_selected=False if length.value != DEFAULT_SUMMARIZATION_LENGTH else True,
        )
        for length in SummarizationLength
    ]
    newspaper_topics: List[NewspaperTopic] = []
    is_refreshing_newspaper_topics: bool = True
    is_refreshing_newspaper: bool = True

    def refreshing_newspaper_topics(self) -> None:
        self.is_refreshing_newspaper_topics = True

    def refresh_user_subscribed_newspaper_topics(self):
        # """Get the news topics."""
        logger.info(f"Refreshing subscribed newspaper topics for user...")
        if self.user and self.user.user_id:
            logger.info(f"User Name: {self.user.name};")
            self.refreshing_newspaper_topics()
            logger.info(
                f"Refreshing news topics for user {self.user.user_id}. Value: {self.is_refreshing_newspaper_topics}..."
            )
            # TODO - to test circular progress
            import time

            time.sleep(2)
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
            self.is_refreshing_newspaper_topics = False
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

    # TODO - remove
    def get_test_newspaper(self) -> Dict[str, Dict[str, List[NewsArticle]]]:
        import time

        time.sleep(2)
        newspaper = {"1": dict(), "2": dict(), "3": dict()}
        newspaper["1"]["2021/01/01"] = [
            NewsArticle(
                article_id="id1_topic1",
                title="Title 1",
                source_urls=["https://www.google.com"],
                published_on_dt="2021-01-01T18:59:24.365373",
                full_summary_text="A full summary text. " * 100,
                medium_summary_text="A medium summary text. " * 50,
                short_summary_text="A short summary text. " * 25,
            ),
            NewsArticle(
                article_id="id2_topic1",
                title="Another title 1",
                source_urls=["https://www.yahoo.com"],
                published_on_dt="2021-01-01T18:57:24.365373",
                full_summary_text="A full summary text 2. " * 100,
                medium_summary_text="A medium summary text 2. " * 50,
                short_summary_text="A short summary text. " * 25,
            ),
        ]
        newspaper["1"]["2021/01/03"] = [
            NewsArticle(
                article_id="id1_topic1",
                title="Title 1",
                source_urls=["https://www.google.com"],
                published_on_dt="2021-01-03T18:59:24.365373",
                full_summary_text="A full different one. " * 100,
                medium_summary_text="A medium different one. " * 50,
                short_summary_text="A short different one. " * 25,
            )
        ]
        newspaper["2"]["2022/03/25"] = [
            NewsArticle(
                article_id="id1_topic2",
                title="Title 2 for this beautiful article",
                source_urls=["https://www.bing.com"],
                published_on_dt="2022-03-25T18:59:24.365373",
                full_summary_text="A full summary text on topic 2. " * 100,
                medium_summary_text="A medium summary text on topic 2. " * 50,
                short_summary_text="A short summary text on topic 2. " * 25,
            )
        ]
        return newspaper

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

    def refresh_newspaper_articles(self):
        """
        Populate the newspaper dictionary per subscribed topic.
        We will load 100 articles per topic to start.
        """
        logger.info(f"Refreshing newspaper articles...")
        newspaper = dict()
        self.is_refreshing_newspaper = True
        if GENERATE_DUMMY_DATA:
            logger.info(f"GENERATE_DUMMY_DATA is set. Getting dummy data")
            newspaper = self.get_test_newspaper()
        else:
            for newspaper_topic in self.newspaper_topics:
                logger.info(
                    f"Refreshing newspaper articles for topic id {newspaper_topic.topic_id}..."
                )
                articles = dict()
                sourced_articles = SourcedArticles.query(newspaper_topic.topic_id, reverse=True)
                while len(newspaper[newspaper_topic.topic_id]) < ARTICLES_PER_PAGE:
                    for sourced_article in sourced_articles:
                        if len(newspaper[newspaper_topic.topic_id]) < ARTICLES_PER_PAGE:
                            date_published = sourced_article.date_published
                            if date_published not in articles:
                                articles[date_published] = []
                            articles[date_published].append(
                                NewsArticle(
                                    article_id=sourced_article.sourced_article_id,
                                    title=sourced_article.title,
                                    source_urls=sourced_article.source_article_urls,
                                    published_on_dt=sourced_article.dt_published.isoformat(),
                                    full_summary_text=get_object(
                                        SOURCED_ARTICLES_S3_BUCKET, sourced_article.full_summary_ref
                                    )[0],
                                    medium_summary_text=get_object(
                                        SOURCED_ARTICLES_S3_BUCKET,
                                        sourced_article.medium_summary_ref,
                                    )[0],
                                    short_summary_text=get_object(
                                        SOURCED_ARTICLES_S3_BUCKET,
                                        sourced_article.short_summary_ref,
                                    )[0],
                                )
                            )
                        else:
                            break
                newspaper[newspaper_topic.topic_id] = articles
        self.newspaper = newspaper
        self.is_refreshing_newspaper = False

    @rx.var
    def get_topic_newspaper_articles(self) -> List[List[Union[str, List[NewsArticle]]]]:
        """Get the newspaper articles for the selected topic sorted by publishing date (latest first)."""
        selected_newspaper_topic = [
            newspaper_topic
            for newspaper_topic in self.newspaper_topics
            if newspaper_topic.is_selected
        ]
        if not selected_newspaper_topic:
            return []
        newspaper_articles = []
        articles_by_date = self.newspaper[selected_newspaper_topic[0].topic_id]
        for published_date, articles in articles_by_date.items():
            newspaper_articles.append([published_date, articles])
        return sorted(newspaper_articles, key=lambda x: x[0], reverse=True)

    @rx.var
    def get_topic_newspaper_articles_no_date(self) -> List[List[NewsArticle]]:
        """Get the newspaper articles for the selected topic sorted by publishing date (latest first)."""
        selected_newspaper_topic = [
            newspaper_topic
            for newspaper_topic in self.newspaper_topics
            if newspaper_topic.is_selected
        ]
        if not selected_newspaper_topic:
            return []
        newspaper_articles = []
        articles_by_date = self.newspaper[selected_newspaper_topic[0].topic_id]
        for published_date, articles in articles_by_date.items():
            newspaper_articles.append([published_date, articles])
        sorted_newspaper_articles = sorted(newspaper_articles, key=lambda x: x[0], reverse=True)
        return [article for _, article in sorted_newspaper_articles]

    @rx.var
    def get_topic_newspaper_articles_published_dates(self) -> List[str]:
        """Get the newspaper articles for the selected topic sorted by publishing date (latest first)."""
        selected_newspaper_topic = [
            newspaper_topic
            for newspaper_topic in self.newspaper_topics
            if newspaper_topic.is_selected
        ]
        if not selected_newspaper_topic:
            return []
        newspaper_published_dates = []
        articles_by_date = self.newspaper[selected_newspaper_topic[0].topic_id]
        for published_date, _ in articles_by_date.items():
            newspaper_published_dates.append(published_date)
        return [
            lexicographic_date_s3_prefix_to_dt(dt_str).strftime("%A, %B %d, %Y")
            for dt_str in sorted(newspaper_published_dates, reverse=True)
        ]

    def on_load_newspaper(self):
        """Load the news topics."""
        logger.info(f"Loading newspaper state...")
        self.refresh_user_subscribed_newspaper_topics()
        self.refresh_newspaper_articles()
