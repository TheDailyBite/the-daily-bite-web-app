from typing import Optional

import reflex as rx
from news_aggregator_data_access_layer.models.dynamodb import (
    NewsTopicSuggestions,
    get_current_dt_utc_attribute,
)

from .base import BaseState


class IndexState(BaseState):
    """Hold the state for the home page."""

    # Whether to show the call to action.
    show_c2a: bool = True
    news_topic_suggestion: Optional[str] = ""

    def close_c2a(self):
        """Close the call to action."""
        self.show_c2a = False
        yield

    def suggest_news_topic(self):
        if self.news_topic_suggestion:
            NewsTopicSuggestions(
                user_id=self.user.user_id,
                topic=self.news_topic_suggestion,
                created_at=get_current_dt_utc_attribute(),
            ).save()
            self.news_topic_suggestion = ""
            yield rx.window_alert("Thank you for your suggestion!")
