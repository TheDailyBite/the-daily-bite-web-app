import pynecone as pc


class ThedailybitewebappConfig(pc.Config):
    pass


config = ThedailybitewebappConfig(
    app_name="the_daily_bite_web_app",
    api_url="0.0.0.0:8000",
    db_url="sqlite:///pynecone.db",
    bun_path="/app/.bun/bin/bun",
)
