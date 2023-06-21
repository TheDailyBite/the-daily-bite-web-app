import pynecone as pc


class ThedailybitewebappConfig(pc.Config):
    pass


config = ThedailybitewebappConfig(
    app_name="the_daily_bite_web_app",
    db_url="sqlite:///pynecone.db",
    env=pc.Env.DEV,
)
