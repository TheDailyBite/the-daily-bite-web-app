"""The News Topics application state."""

from typing import Any, Dict, List, Optional, Tuple, Union

import asyncio
from datetime import datetime, timedelta, timezone

import reflex as rx
from news_aggregator_data_access_layer.config import SOURCED_ARTICLES_S3_BUCKET
from news_aggregator_data_access_layer.constants import ArticleApprovalStatus, SummarizationLength
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

from the_daily_bite_web_app.config import (
    ARTICLES_PER_PAGE,
    GENERATE_DUMMY_DATA,
    MAX_SOURCES_PER_ARTICLE_IN_UI,
    NEWSPAPER_REFRESH_FREQUENCY_MINS,
)

from .base import BaseState
from .models import ArticleSummarizationLength, NewsArticle, NewspaperTopic

logger = setup_logger(__name__)

DEFAULT_SUMMARIZATION_LENGTH = SummarizationLength.SHORT.value


class NewspaperState(BaseState):
    """The newspaper state."""

    # will be topic id: published date: list of articles
    newspaper: Dict[str, Dict[str, List[NewsArticle]]] = dict()
    # will be topic id: published date: (expected number of articles, current number of articles)
    # ideally we'd load this asynchronously
    # newspaper_inventory_tracker: Dict[str, Dict[str, int]] = dict()
    article_summarization_lengths: List[ArticleSummarizationLength] = [
        ArticleSummarizationLength(
            summarization_length=length.value,
            is_selected=False if length.value != DEFAULT_SUMMARIZATION_LENGTH else True,
        )
        for length in SummarizationLength
    ]
    newspaper_topics: List[NewspaperTopic] = []
    is_refreshing_newspaper_topics: bool = True
    topic_newspaper_refresh_status: Dict[str, bool] = dict()
    is_loading_more_articles: bool = False
    # <topic_id>: <last_evaluated_key> to allow us to page through results
    _last_fetched_newspaper_article_by_topic: Dict[str, Dict[str, Dict[str, Any]]] = dict()
    # <topic_id>: <datetime> to allow us to keep track of the last time we refreshed the newspaper per topic
    _last_newspaper_refresh_dt_by_topic: Dict[str, datetime] = dict()

    async def refresh_user_subscribed_newspaper_topics(self):
        # """Get the news topics."""
        logger.info(f"Refreshing subscribed newspaper topics for user...")
        if self.user and self.user.user_id:
            logger.info(f"User Name: {self.user.name};")
            self.set_is_refreshing_newspaper_topics(True)
            yield
            logger.info(
                f"Refreshing news topics for user {self.user.user_id}. Value: {self.is_refreshing_newspaper_topics}..."
            )
            # TODO - can remove this
            if GENERATE_DUMMY_DATA:
                # TODO - to test circular progress
                await asyncio.sleep(2)
                logger.info(f"GENERATE_DUMMY_DATA is set. Getting dummy data for newspaper topics.")
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
            for newspaper_topic in self.newspaper_topics:
                if newspaper_topic.topic_id not in self.topic_newspaper_refresh_status:
                    self.topic_newspaper_refresh_status[newspaper_topic.topic_id] = True
            logger.info(f"Done getting newspaper topics for user {self.user.user_id}...")
            self.set_is_refreshing_newspaper_topics(False)
            yield
        else:
            logger.warning(f"User is not logged in. Cannot get news topics")

    # TODO - remove
    def get_test_user_newspaper_topics(self) -> List[NewspaperTopic]:
        return [
            NewspaperTopic(
                topic_id="1",
                topic="Topic 1",
                is_selected=True,
            ),
            NewspaperTopic(
                topic_id="2",
                topic="Topic 2",
                is_selected=False,
            ),
            NewspaperTopic(
                topic_id="3",
                topic="Topic 3",
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
                source_urls=["https://www.google.com", "https://www.yahoo.com"],
                published_on_dt="2021-01-01T18:59:24.365373",
                full_summary_text="A full summary text. " * 100,
                medium_summary_text="A medium summary text. " * 50,
                short_summary_text=(("A short summary text. " * 10 + "\n\n") * 2).replace(
                    "\n", "<br>"
                ),
            ),
            NewsArticle(
                article_id="id2_topic1",
                title="Another title 1",
                source_urls=["https://www.yahoo.com"],
                published_on_dt="2021-01-01T18:57:24.365373",
                full_summary_text="A full summary text 2. " * 100,
                medium_summary_text="A medium summary text 2. " * 50,
                short_summary_text=(("A short summary text. " * 10 + "\n\n") * 2).replace(
                    "\n", "<br>"
                ),
            ),
            NewsArticle(
                article_id="id3_topic1",
                title="Another title 1.1",
                source_urls=["https://www.yahoo.com"],
                published_on_dt="2021-01-01T18:55:24.365373",
                full_summary_text="A full summary text 2. " * 100,
                medium_summary_text="A medium summary text 2. " * 50,
                short_summary_text=(("A short summary text. " * 10 + "\n\n") * 2).replace(
                    "\n", "<br>"
                ),
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
            ),
            NewsArticle(
                article_id="id2_topic2",
                title="Title 2 for this beautiful article",
                source_urls=["https://www.bing.com"],
                published_on_dt="2022-03-25T18:59:24.365373",
                full_summary_text="A full summary text on topic 2. " * 100,
                medium_summary_text="A medium summary text on topic 2. " * 50,
                short_summary_text="A short summary text on topic 2. " * 25,
            ),
            NewsArticle(
                article_id="id2_topic2",
                title="Title 2 for this beautiful article",
                source_urls=["https://www.bing.com"],
                published_on_dt="2022-03-25T18:59:24.365373",
                full_summary_text="A full summary text on topic 2. " * 100,
                medium_summary_text="A medium summary text on topic 2. " * 50,
                short_summary_text="A short summary text on topic 2. " * 25,
            ),
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

    @rx.var
    def has_subscribed_newspaper_topics(self) -> bool:
        return len(self.newspaper_topics) > 0

    def newspaper_topic_selected(self, idx: int):
        """Set the selected newspaper topic."""
        for i, newspaper_topic in enumerate(self.newspaper_topics):
            if i == idx:
                newspaper_topic.is_selected = True
                selected_topic_id = newspaper_topic.topic_id
            else:
                newspaper_topic.is_selected = False
        if selected_topic_id not in self.newspaper:
            self.load_articles_for_topic(selected_topic_id, count=ARTICLES_PER_PAGE)
        # NOTE - this is a temporary workaround to ensure the frontend receives the updated state
        self.newspaper_topics = self.newspaper_topics

    def get_selected_newspaper_topic_id(self) -> Optional[str]:
        selected_newspaper_topic = [
            newspaper_topic
            for newspaper_topic in self.newspaper_topics
            if newspaper_topic.is_selected
        ]
        if not selected_newspaper_topic:
            return None
        return selected_newspaper_topic[0].topic_id

    async def load_more_articles(self):
        """Load more articles for the selected newspaper topic."""
        selected_newspaper_topic = [topic for topic in self.newspaper_topics if topic.is_selected][
            0
        ]
        if selected_newspaper_topic:
            self.set_is_loading_more_articles(True)
            yield
            logger.info(f"Loading more articles for topic: {selected_newspaper_topic.topic}")
            if not GENERATE_DUMMY_DATA:
                self.load_articles_for_topic(
                    selected_newspaper_topic.topic_id, count=ARTICLES_PER_PAGE
                )
            else:
                logger.info(f"Sleeping for 5 seconds to simulate loading more articles...")
                await asyncio.sleep(5)
            self.set_is_loading_more_articles(False)
            yield

    @rx.var
    def get_selected_article_summarization_length(self) -> ArticleSummarizationLength:
        """Get the selected article summarization length."""
        selected_article_summarization_length = None
        for article_summarization_length in self.article_summarization_lengths:
            if article_summarization_length.is_selected:
                selected_article_summarization_length = article_summarization_length
                return selected_article_summarization_length

    @rx.var
    def is_refreshing_selected_newspaper_topic(self) -> bool:
        """Get whether the selected newspaper topic is refreshing."""
        selected_newspaper_topic_id = self.get_selected_newspaper_topic_id()
        if not selected_newspaper_topic_id:
            return False
        return self.topic_newspaper_refresh_status.get(selected_newspaper_topic_id, False)

    async def refresh_selected_topic_newspaper_articles(self):
        """
        Populate the newspaper dictionary for the selected subscribed topic.
        """
        selected_topic_id = self.get_selected_newspaper_topic_id()
        if not selected_topic_id:
            logger.info(f"No selected topic. Nothing to do.")
            return
        logger.info(f"Refreshing newspaper articles {selected_topic_id}...")
        # have refreshed within the last NEWSPAPER_REFRESH_FREQUENCY_MINS minutes
        if self._last_newspaper_refresh_dt_by_topic.get(selected_topic_id) and datetime.now(
            tz=timezone.utc
        ) - self._last_newspaper_refresh_dt_by_topic[selected_topic_id] < timedelta(
            minutes=NEWSPAPER_REFRESH_FREQUENCY_MINS
        ):
            return
        self.newspaper[selected_topic_id] = dict()
        self._last_fetched_newspaper_article_by_topic[selected_topic_id] = dict()
        self.topic_newspaper_refresh_status[selected_topic_id] = True
        yield
        if GENERATE_DUMMY_DATA:
            logger.info(
                f"GENERATE_DUMMY_DATA is set. Getting dummy data for refresh newspaper articles."
            )
            self.newspaper = self.get_test_newspaper()
        logger.info(f"Refreshing newspaper articles for topic id {selected_topic_id}...")
        self.load_articles_for_topic(selected_topic_id, count=ARTICLES_PER_PAGE)
        self.topic_newspaper_refresh_status[selected_topic_id] = False
        yield
        self._last_newspaper_refresh_dt_by_topic[selected_topic_id] = datetime.now(tz=timezone.utc)
        yield

    def load_newest_articles(self, topic_id: str):
        # an idea is to simply have a last evaluated key in the scan_index_forward=True direction as well
        # This will be set to the newest article in the newspaper at the first refresh
        # after that it will go on autopilot and keep the newest as the last evaluated key, until None is reached.
        # Another option... we can also just
        pass

    def load_articles_for_topic(self, topic_id: str, count: int):
        """
        Load articles for the given topic id.
        NOTE - TODO - this approach is naive since it wouldn't work as expected with articles which are approved after the initial load.
        Also currently load_newest_articles is not implemented.
        An option is in the background to use PublishedArticles table and keep track of the expected and actual count
        and load articles in the newspaper to make sure that at some point these match.
        """
        logger.info(f"Loading {count} articles for topic id {topic_id}...")
        # TODO
        # load_newest_articles(topic_id)
        SOME_MAGIC_LAST_EVALUATED_KEY_STRING = "mAgIcLaStEvAlUaTeDkEy"
        last_evaluated_key = self._last_fetched_newspaper_article_by_topic.get(
            topic_id, SOME_MAGIC_LAST_EVALUATED_KEY_STRING
        )
        # if it is None in the _last_fetched_newspaper_article_by_topic it means we've processed all articles for this topic
        # so we're done
        if last_evaluated_key is not None:
            articles = dict()
            if last_evaluated_key == SOME_MAGIC_LAST_EVALUATED_KEY_STRING:
                # means we've never loaded articles for this topic so we set last evaluated key to None to start
                last_evaluated_key = None
            sourced_articles = SourcedArticles.query(
                topic_id,
                scan_index_forward=False,
                filter_condition=SourcedArticles.article_approval_status
                == ArticleApprovalStatus.APPROVED,
                last_evaluated_key=last_evaluated_key,
            )
            articles_loaded = 0
            for sourced_article in sourced_articles:
                date_published = sourced_article.date_published
                if date_published not in articles:
                    articles[date_published] = []
                articles[date_published].append(
                    NewsArticle(
                        article_id=sourced_article.sourced_article_id,
                        title=sourced_article.title,
                        source_urls=sourced_article.source_article_urls[
                            :MAX_SOURCES_PER_ARTICLE_IN_UI
                        ],
                        source_provider_names=sourced_article.providers[
                            :MAX_SOURCES_PER_ARTICLE_IN_UI
                        ],
                        published_on_dt=sourced_article.dt_published.strftime("%Y-%m-%d %H:%M:%S"),
                        full_summary_text=get_object(
                            SOURCED_ARTICLES_S3_BUCKET, sourced_article.full_summary_ref
                        )[0].replace("\n", "<br>"),
                        medium_summary_text=get_object(
                            SOURCED_ARTICLES_S3_BUCKET,
                            sourced_article.medium_summary_ref,
                        )[0].replace("\n", "<br>"),
                        short_summary_text=get_object(
                            SOURCED_ARTICLES_S3_BUCKET,
                            sourced_article.short_summary_ref,
                        )[0].replace("\n", "<br>"),
                    )
                )
                articles_loaded += 1
                if articles_loaded >= count:
                    break
            if topic_id not in self.newspaper:
                self.newspaper[topic_id] = articles
            else:
                for date_published, articles_on_date in articles.items():
                    if date_published not in self.newspaper[topic_id]:
                        self.newspaper[topic_id][date_published] = []
                    self.newspaper[topic_id][date_published].extend(articles_on_date)
            last_evaluated_key = sourced_articles.last_evaluated_key
            logger.info(
                f"Topic Id: {topic_id}; Current Last Evaluated Key: {self._last_fetched_newspaper_article_by_topic.get(topic_id)} Last Evaluated Key: {last_evaluated_key}"
            )
            logger.info(f"Setting last evaluated key for topic id {topic_id}...")
            self._last_fetched_newspaper_article_by_topic[topic_id] = last_evaluated_key

    @rx.var
    def get_selected_topic_name(self) -> str:
        selected_newspaper_topic = [
            newspaper_topic
            for newspaper_topic in self.newspaper_topics
            if newspaper_topic.is_selected
        ]
        if not selected_newspaper_topic:
            return ""
        return selected_newspaper_topic[0].topic

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
        selected_newspaper_topic_id = selected_newspaper_topic[0].topic_id
        newspaper_articles = []
        if selected_newspaper_topic_id not in self.newspaper:
            return []
        articles_by_date = self.newspaper[selected_newspaper_topic_id]
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
        selected_newspaper_topic_id = selected_newspaper_topic[0].topic_id
        newspaper_published_dates = []
        if selected_newspaper_topic_id not in self.newspaper:
            return []
        articles_by_date = self.newspaper[selected_newspaper_topic_id]
        for published_date, _ in articles_by_date.items():
            newspaper_published_dates.append(published_date)
        return [
            lexicographic_date_s3_prefix_to_dt(dt_str).strftime("%A, %B %d, %Y")
            for dt_str in sorted(newspaper_published_dates, reverse=True)
        ]

    def on_load_newspaper(self):
        """Load the news topics."""
        logger.info(f"Loading newspaper state...")
        yield NewspaperState.refresh_user_subscribed_newspaper_topics()
        yield NewspaperState.refresh_selected_topic_newspaper_articles()
