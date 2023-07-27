from typing import Optional

import reflex as rx
from news_aggregator_data_access_layer.models.dynamodb import PreviewUsers

from .base import BaseState


class NewsletterState(BaseState):
    email: str = ""
    newsletter_interest_signed_up: bool = False

    def newsletter_interest_signup(self):
        if self.user and self.user.user_id and self.email:
            user = PreviewUsers.get(self.user.user_id)
            user.update(
                actions=[
                    PreviewUsers.newsletter_interest_email.set(self.email),
                ]
            )
            self.email = ""
            self.newsletter_interest_signed_up = True
            return rx.window_alert("You're on the waitlist. Thank you for your interest!")
