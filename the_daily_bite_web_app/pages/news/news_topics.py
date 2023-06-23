import pynecone as pc

from the_daily_bite_web_app import constants, styles
from the_daily_bite_web_app.templates import webpage


@webpage(path="/news-topics")
def news_topics() -> pc.Component:
    """Get the news topics page."""
    return pc.fragment(
        pc.color_mode_button(pc.color_mode_icon(), float="right"),
        pc.vstack(
            pc.heading("Welcome to News Topics page!", font_size="2em"),
            spacing="1.5em",
            font_size="2em",
            padding_top="10%",
        ),
    )
