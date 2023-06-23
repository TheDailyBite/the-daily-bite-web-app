"""The base application state."""

from typing import Optional

import pynecone as pc

from the_daily_bite_web_app.constants import LOGIN_PATH

from .models import User


class BaseState(pc.State):
    """The base state."""

    user: Optional[User] = None

    def log_out(self):
        self.reset()
        return pc.redirect(LOGIN_PATH)

    def verify_login(self):
        """Check if a user is logged in."""
        if not self.logged_in:
            return pc.redirect(LOGIN_PATH)

    @pc.var
    def logged_in(self):
        """Check if a user is logged in."""
        return self.user is not None
