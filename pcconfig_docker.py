import os

import pynecone as pc


class ThedailybitewebappConfig(pc.Config):
    pass


PORT = os.environ.get("PORT", "8000")
HOST = os.environ.get("HOST", "http://0.0.0.0")

config = ThedailybitewebappConfig(
    app_name="the_daily_bite_web_app",
    api_url=f"{HOST}:{PORT}",
    bun_path="/app/.bun/bin/bun",
)
