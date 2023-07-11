"""The base application state."""

from typing import Optional

import reflex as rx

from the_daily_bite_web_app.config import GENERATE_DUMMY_DATA
from the_daily_bite_web_app.constants import LOGIN_PATH

from .models import User


class BaseState(rx.State):
    """The base state."""

    user: Optional[User] = (
        None if not GENERATE_DUMMY_DATA else User(user_id="abc", name="Michael the Admin")
    )

    def log_out(self):
        self.reset()
        return rx.redirect(LOGIN_PATH)

    def verify_login(self):
        """Check if a user is logged in."""
        if not self.logged_in:
            return rx.redirect(LOGIN_PATH)

    @rx.var
    def logged_in(self):
        """Check if a user is logged in."""
        return self.user is not None

    @rx.var
    def user_name(self):
        """Get the user name."""
        return self.user.name if self.user else ""
