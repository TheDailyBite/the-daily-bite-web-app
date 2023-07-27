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
    topic_id: str
    source_urls: List[str]
    source_provider_names: List[str]
    # this is the publishing date for the ui
    published_on_dt: str
    # this is the publishing date of the newspaper it is part of (e.g. 2022/01/01)
    date_published: str
    full_summary_text: Optional[str]
    show_full_summary_text: bool = False
    full_summary_ref: str
    medium_summary_text: Optional[str]
    show_medium_summary_text: bool = False
    medium_summary_ref: str
    short_summary_text: Optional[str]
    show_short_summary_text: bool = False
    short_summary_ref: str
    show_article: bool = False


class NewspaperTopic(rx.Model):
    topic_id: str
    topic: str
    is_selected: bool
