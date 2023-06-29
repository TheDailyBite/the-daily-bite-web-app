from typing import Optional

import pynecone as pc


class User(pc.Model):
    user_id: str
    name: str


class NewsTopic(pc.Model):
    topic_id: str
    topic: str
    category: Optional[str]
    last_publishing_date: Optional[str]
    is_user_subscribed: bool
    is_selected: bool = False


class NewsArticle(pc.Model):
    article_id: str
    title: str
    full_summary_text: str
    medium_summary_text: str
    short_summary_text: str


class ArticleSummarizationLength(pc.Model):
    summarization_length: str
    is_selected: bool


class NewspaperTopic(pc.Model):
    topic_id: str
    topic: str
    category: Optional[str]
    is_selected: bool
