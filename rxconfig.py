import reflex as rx


class ThedailybitewebappConfig(rx.Config):
    pass


config = ThedailybitewebappConfig(
    app_name="the_daily_bite_web_app",
    env=rx.Env.DEV,
)
