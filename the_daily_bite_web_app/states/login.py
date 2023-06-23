import pynecone as pc

from the_daily_bite_web_app.constants import INDEX_PATH

from .base import BaseState
from .models import User


class LoginState(BaseState):
    """State for the login form."""

    user_id_field: str = ""

    def log_in(self):
        if self.user_id_field == "b6d8665a-99a9-40d5-b6de-d8db97405329":
            user = User(user_id=self.user_id_field, name="John Doe")
            self.user = user
            return pc.redirect(INDEX_PATH)
        else:
            return pc.window_alert("Wrong username or password.")
