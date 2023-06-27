import pynecone as pc

from the_daily_bite_web_app.config import NEWS_SERVICE_LOGIN_URL, USER_LOGIN_FUNCTION_NAME
from the_daily_bite_web_app.constants import INDEX_PATH
from the_daily_bite_web_app.exceptions import InvokeFunctionException
from the_daily_bite_web_app.utils.aws_lambda import invoke_function
from the_daily_bite_web_app.utils.telemetry import setup_logger

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
            if self.user_id_field == "21286987-0dd3-44c1-88b6-a8361e37823c":
                user = User(user_id=self.user_id_field, name="Michael the Admin")
                logger.info("Logged in as %s.", user.name)
                self.user = user
                return pc.redirect(INDEX_PATH)
            try:
                response = invoke_function(
                    USER_LOGIN_FUNCTION_NAME,
                    {"user_id": self.user_id_field},
                    function_url=NEWS_SERVICE_LOGIN_URL,
                )
                if response["statusCode"] == 200:
                    body = response["body"]
                    user = User(user_id=self.user_id_field, name=body["name"])
                    logger.info("Logged in as %s.", user.name)
                    self.user = user
                    return pc.redirect(INDEX_PATH)
            except (InvokeFunctionException, Exception):
                return pc.window_alert("Error logging in. Please try again.")
        return pc.window_alert(
            "Wrong user id. Make sure you have been added to the preview of the service."
        )
