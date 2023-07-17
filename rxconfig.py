import reflex as rx
from news_aggregator_data_access_layer.utils.telemetry import setup_logger

from the_daily_bite_web_app import config

logger = setup_logger(__name__)


class ThedailybitewebappConfig(rx.Config):
    pass


api_url = f"{config.BACKEND_HOST}:{config.BACKEND_PORT}"
logger.info(f"api_url: {api_url}")

config = ThedailybitewebappConfig(
    app_name="the_daily_bite_web_app",
    api_url=api_url,
    env=rx.Env.PROD,
)
