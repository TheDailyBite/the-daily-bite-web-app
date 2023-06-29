import pynecone as pc

from the_daily_bite_web_app.constants import INDEX_PATH
from the_daily_bite_web_app.utils.aws_lambda import invoke_function
from the_daily_bite_web_app.utils.telemetry import setup_logger
from news_aggregator_data_access_layer.models.dynamodb import (
    PreviewUsers,
)

from .base import BaseState
from .models import User

logger = setup_logger(__name__)


class LoginState(BaseState):
    """State for the login form."""

    user_id_field: str = ""

    def log_in(self):
        logger.info(f"Logging in with user id {self.user_id_field}...")
        if self.user_id_field:
            # TODO - remove this. It is temporary and allows for local testing
            if self.user_id_field == "abc": # "21286987-0dd3-44c1-88b6-a8361e37823c":
                user = User(user_id=self.user_id_field, name="Michael the Admin")
                logger.info("Logged in as %s.", user.name)
                self.user = user
                return pc.redirect(INDEX_PATH)
            try:
                preview_user = PreviewUsers.get(self.user_id_field)
                user = User(user_id=preview_user.user_id, name=preview_user.name)
                logger.info("Logged in as %s.", user.name)
                self.user = user
                return pc.redirect(INDEX_PATH)
            except PreviewUsers.DoesNotExist:
                return pc.window_alert(
                    "Wrong user id. Make sure you have been added to the preview of the service."
                )
            except Exception as e:
                return pc.window_alert("Error logging in. Please try again.")
        return pc.window_alert(
            "Wrong user id. Make sure you have been added to the preview of the service."
        )
