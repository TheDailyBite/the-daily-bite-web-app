from typing import List, Optional

import reflex as rx


class User(rx.Model):
    user_id: str
    name: str


class NewsTopic(rx.Model):
    topic_id: str
    topic: str
    last_publishing_date: Optional[str]
    is_user_subscribed: bool
    is_selected: bool = False


class NewsArticle(rx.Model):
    article_id: str
    title: str
    source_urls: List[str]
    published_on_dt: str
    full_summary_text: str
    medium_summary_text: str
    short_summary_text: str


class ArticleSummarizationLength(rx.Model):
    summarization_length: str
    is_selected: bool


class NewspaperTopic(rx.Model):
    topic_id: str
    topic: str
    is_selected: bool
