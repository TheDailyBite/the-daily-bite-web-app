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
