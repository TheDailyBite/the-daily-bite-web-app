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
    MAX_SOURCES_PER_ARTICLE_IN_UI,
    NEWSPAPER_REFRESH_FREQUENCY_MINS,
)

from .base import BaseState
from .models import NewsArticle, NewspaperTopic

logger = setup_logger(__name__)


class NewspaperState(BaseState):
    """The newspaper state."""

    # will be topic id: published date: list of articles
    newspaper: Dict[str, Dict[str, List[NewsArticle]]] = dict()
    # will be topic id: published date: (expected number of articles, current number of articles)
    # ideally we'd load this asynchronously
    # newspaper_inventory_tracker: Dict[str, Dict[str, int]] = dict()
    newspaper_topics: List[NewspaperTopic] = []
    is_refreshing_newspaper_topics: bool = True
    topic_newspaper_refresh_status: Dict[str, bool] = dict()
    is_loading_more_articles: bool = False
    # <topic_id>: <last_evaluated_key> to allow us to page through results
    _last_fetched_newspaper_article_by_topic: Dict[str, Dict[str, Dict[str, Any]]] = dict()
    # <topic_id>: <datetime> to allow us to keep track of the last time we refreshed the newspaper per topic
    _last_newspaper_refresh_dt_by_topic: Dict[str, datetime] = dict()
    selected_newspaper_topic_id: str = ""

    def refresh_user_subscribed_newspaper_topics(self):
        # """Get the news topics."""
        if self.user and self.user.user_id:
            logger.info(f"User Name: {self.user.name};")
            self.set_is_refreshing_newspaper_topics(True)
            yield
            logger.info(
                f"Refreshing news topics for user {self.user.user_id}. Value: {self.is_refreshing_newspaper_topics}..."
            )
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
            finally:
                logger.info(f"Done getting newspaper topics for user {self.user.user_id}...")
                self.set_is_refreshing_newspaper_topics(False)
                yield
                if self.newspaper_topics:
                    if (
                        not self.selected_newspaper_topic_id
                        or self.selected_newspaper_topic_id
                        not in [
                            newspaper_topic.topic_id for newspaper_topic in self.newspaper_topics
                        ]
                    ):
                        # we take the first topic as the selected topic
                        self.selected_newspaper_topic_id = self.newspaper_topics[0].topic_id
                        yield
                for newspaper_topic in self.newspaper_topics:
                    topic_id = newspaper_topic.topic_id
                    if topic_id not in self.newspaper:
                        self.newspaper[topic_id] = dict()
                    if topic_id not in self.topic_newspaper_refresh_status:
                        self.topic_newspaper_refresh_status[topic_id] = False
                    if topic_id not in self._last_fetched_newspaper_article_by_topic:
                        self._last_fetched_newspaper_article_by_topic[topic_id] = dict()
                    if topic_id not in self._last_newspaper_refresh_dt_by_topic:
                        self._last_newspaper_refresh_dt_by_topic[topic_id] = datetime.min.replace(
                            tzinfo=timezone.utc
                        )
                return
        else:
            logger.warning(f"User is not logged in. Cannot get news topics")

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
                self.selected_newspaper_topic_id = newspaper_topic.topic_id
            else:
                newspaper_topic.is_selected = False

    def load_more_articles(self):
        """Load more articles for the selected newspaper topic."""
        if self.selected_newspaper_topic_id:
            self.set_is_loading_more_articles(True)
            yield
            logger.info(
                f"Loading more articles for topic id: {self.selected_newspaper_topic_id}..."
            )
            self.load_articles_for_topic(self.selected_newspaper_topic_id, count=ARTICLES_PER_PAGE)
            self.set_is_loading_more_articles(False)
            yield

    @rx.var
    def is_refreshing_selected_newspaper_topic(self) -> bool:
        """Get whether the selected newspaper topic is refreshing."""
        return self.topic_newspaper_refresh_status.get(self.selected_newspaper_topic_id, False)

    def refresh_selected_topic_newspaper_articles(self):
        """
        Populate the newspaper dictionary for the selected subscribed topic.
        """
        selected_topic_id = self.selected_newspaper_topic_id
        if not selected_topic_id:
            logger.info(f"No selected topic. Nothing to do.")
            return
        logger.info(f"Refreshing newspaper articles {selected_topic_id}...")
        # have refreshed within the last NEWSPAPER_REFRESH_FREQUENCY_MINS minutes
        now_dt = datetime.now(tz=timezone.utc)
        last_refresh_dt = self._last_newspaper_refresh_dt_by_topic[selected_topic_id]
        timedelta_since_last_refresh = now_dt - last_refresh_dt
        if timedelta_since_last_refresh < timedelta(minutes=NEWSPAPER_REFRESH_FREQUENCY_MINS):
            logger.info(
                f"Newspaper articles for topic id {selected_topic_id} were refreshed {timedelta_since_last_refresh} time ago. Skipping..."
            )
            return
        # TODO - here
        self.topic_newspaper_refresh_status[selected_topic_id] = True
        yield
        self.newspaper[selected_topic_id] = dict()
        self._last_fetched_newspaper_article_by_topic[selected_topic_id] = dict()
        self.load_articles_for_topic(selected_topic_id, count=ARTICLES_PER_PAGE)
        yield
        self._last_newspaper_refresh_dt_by_topic[selected_topic_id] = datetime.now(tz=timezone.utc)
        yield
        self.topic_newspaper_refresh_status[selected_topic_id] = False
        yield

    def find_newspaper_article(self, article: NewsArticle) -> Optional[NewsArticle]:
        if not isinstance(article, NewsArticle):
            raise TypeError(f"Expected NewsArticle, got {type(article)}")
        articles = self.newspaper[article.topic_id][article.date_published]
        for a in articles:
            if a.article_id == article.article_id:
                return a
        return None

    def set_show_article_property(self, article: NewsArticle, show_article: bool):
        article = NewsArticle.parse_obj(article)
        # could emit metrics here for the article
        self.find_newspaper_article(article).show_article = show_article
        # NOTE - this is a temporary workaround to ensure the frontend receives the updated state
        self.newspaper = self.newspaper
        return

    def set_show_length_property(self, article: NewsArticle, show_length: Optional[str] = None):
        article = NewsArticle.parse_obj(article)
        newspaper_article = self.find_newspaper_article(article)
        if (
            not newspaper_article.show_short_summary_text
            and not newspaper_article.show_medium_summary_text
            and not newspaper_article.show_full_summary_text
        ):
            newspaper_article.show_short_summary_text = True
        # has a value set; change it
        elif show_length:
            if show_length == SummarizationLength.SHORT.value:
                newspaper_article.show_short_summary_text = True
                newspaper_article.show_medium_summary_text = False
                newspaper_article.show_full_summary_text = False
            elif show_length == SummarizationLength.MEDIUM.value:
                newspaper_article.show_medium_summary_text = True
                newspaper_article.show_short_summary_text = False
                newspaper_article.show_full_summary_text = False
            elif show_length == SummarizationLength.FULL.value:
                newspaper_article.show_full_summary_text = True
                newspaper_article.show_short_summary_text = False
                newspaper_article.show_medium_summary_text = False
        # NOTE - this is a temporary workaround to ensure the frontend receives the updated state
        self.newspaper = self.newspaper
        return

    def load_newest_articles(self, topic_id: str):
        # an idea is to simply have a last evaluated key in the scan_index_forward=True direction as well
        # This will be set to the newest article in the newspaper at the first refresh
        # after that it will go on autopilot and keep the newest as the last evaluated key, until None is reached.
        # Another option... we can also just
        pass

    def populate_article_text(self, article: NewsArticle) -> None:
        def get_text(ref: str) -> str:
            return get_object(
                SOURCED_ARTICLES_S3_BUCKET,
                ref,
            )[
                0
            ].replace("\n", "<br>")

        article = NewsArticle.parse_obj(article)
        newspaper_article = self.find_newspaper_article(article)
        if newspaper_article.show_short_summary_text:
            if newspaper_article.short_summary_text:
                return
            text = get_text(newspaper_article.short_summary_ref)
            newspaper_article.short_summary_text = text
        elif newspaper_article.show_medium_summary_text:
            if newspaper_article.medium_summary_text:
                return
            text = get_text(newspaper_article.medium_summary_ref)
            newspaper_article.medium_summary_text = text
        elif newspaper_article.show_full_summary_text:
            if newspaper_article.full_summary_text:
                return
            text = get_text(newspaper_article.full_summary_ref)
            newspaper_article.full_summary_text = text
        # NOTE - this is a temporary workaround to ensure the frontend receives the updated state
        self.newspaper = self.newspaper

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

        last_evaluated_key = self._last_fetched_newspaper_article_by_topic[topic_id]
        # if it is None in the _last_fetched_newspaper_article_by_topic it means we've processed all articles for this topic
        # so we're done
        if last_evaluated_key is not None:
            articles = dict()
            if last_evaluated_key == dict():
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
                        topic_id=sourced_article.topic_id,
                        source_urls=sourced_article.source_article_urls[
                            :MAX_SOURCES_PER_ARTICLE_IN_UI
                        ],
                        source_provider_names=sourced_article.providers[
                            :MAX_SOURCES_PER_ARTICLE_IN_UI
                        ],
                        date_published=date_published,
                        published_on_dt=sourced_article.dt_published.strftime("%Y-%m-%d %H:%M:%S"),
                        full_summary_ref=sourced_article.full_summary_ref,
                        medium_summary_ref=sourced_article.medium_summary_ref,
                        short_summary_ref=sourced_article.short_summary_ref,
                    )
                )
                articles_loaded += 1
                if articles_loaded >= count:
                    break
            for date_published, articles_on_date in articles.items():
                if date_published not in self.newspaper[topic_id]:
                    self.newspaper[topic_id][date_published] = []
                self.newspaper[topic_id][date_published].extend(articles_on_date)
            last_evaluated_key = sourced_articles.last_evaluated_key
            logger.info(
                f"Topic Id: {topic_id}; Current Last Evaluated Key: {self._last_fetched_newspaper_article_by_topic.get(topic_id)} Last Evaluated Key: {last_evaluated_key}"
            )
            self._last_fetched_newspaper_article_by_topic[topic_id] = last_evaluated_key

    @rx.var
    def get_selected_topic_name(self) -> str:
        selected_newspaper_topic = [
            newspaper_topic
            for newspaper_topic in self.newspaper_topics
            if newspaper_topic.topic_id == self.selected_newspaper_topic_id
        ]
        if not selected_newspaper_topic:
            return ""
        return selected_newspaper_topic[0].topic

    @rx.var
    def get_topic_newspaper_articles_no_date(self) -> List[List[NewsArticle]]:
        """Get the newspaper articles for the selected topic sorted by publishing date (latest first)."""
        newspaper_articles = []
        if not self.selected_newspaper_topic_id:
            return []
        if self.selected_newspaper_topic_id not in self.newspaper:
            return []
        articles_by_date = self.newspaper[self.selected_newspaper_topic_id]
        for published_date, articles in articles_by_date.items():
            newspaper_articles.append([published_date, articles])
        sorted_newspaper_articles = sorted(newspaper_articles, key=lambda x: x[0], reverse=True)
        return [article for _, article in sorted_newspaper_articles]

    @rx.var
    def get_topic_newspaper_articles_published_dates(self) -> List[str]:
        """Get the newspaper articles for the selected topic sorted by publishing date (latest first)."""
        newspaper_published_dates: List[str] = []
        if self.selected_newspaper_topic_id not in self.newspaper:
            return newspaper_published_dates
        articles_by_date = self.newspaper[self.selected_newspaper_topic_id]
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
        # TODO - is right?
