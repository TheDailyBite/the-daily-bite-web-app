import reflex as rx

from the_daily_bite_web_app import constants, styles
from the_daily_bite_web_app.constants import (
    CONTACT_URL,
    INDEX_PATH,
    NEWS_TOPICS_PATH,
    NEWSPAPER_PATH,
    TITLE,
)
from the_daily_bite_web_app.states import IndexState
from the_daily_bite_web_app.templates import webpage


def list_circle(text):
    return rx.flex(
        rx.text(text),
        width="20px",
        height="20px",
        border_radius="6px",
        bg="#F5EFFE",
        color="#5646ED",
        align_items="center",
        justify_content="center",
        font_weight="800",
    )


def landing():
    return rx.container(
        rx.vstack(
            rx.box(
                rx.text(
                    "News. Daily.",
                    font_size=styles.HERO_FONT_SIZE,
                    font_weight=700,
                    font_family=styles.TEXT_FONT_FAMILY,
                ),
                rx.text(
                    "Bite Sized.",
                    font_size=styles.HERO_FONT_SIZE,
                    font_weight=700,
                    font_family=styles.TEXT_FONT_FAMILY,
                ),
                rx.text(
                    "Find your favorite news topics, or suggest a new one for us to track.",
                    font_size=styles.HERO_FONT_SIZE,
                    font_weight=800,
                    font_family=styles.TEXT_FONT_FAMILY,
                    background_image=styles.LINEAR_GRADIENT_TEXT_BACKGROUND,
                    background_clip="text",
                ),
                text_align="center",
                line_height="1.15",
            ),
            rx.container(
                "Read informative news on the daily, in a reasonable amount of time.",
                color="grey",
                font_size="1.1em",
                font_family=styles.TEXT_FONT_FAMILY,
                text_align="center",
            ),
            rx.divider(),
            rx.box(
                rx.center(
                    "How it works",
                    font_size=styles.H2_FONT_SIZE,
                    font_weight=600,
                    font_family=styles.TEXT_FONT_FAMILY,
                ),
                rx.divider(),
                rx.hstack(
                    list_circle("1"),
                    rx.text(
                        rx.link(
                            "Subscribe to news topics",
                            href=NEWS_TOPICS_PATH,
                            font_family=styles.TEXT_FONT_FAMILY,
                        ),
                        " that you're interested in reading about...",
                        font_family=styles.TEXT_FONT_FAMILY,
                    ),
                ),
                rx.hstack(
                    list_circle("2"),
                    rx.text(
                        rx.link(
                            "The Newspaper",
                            href=NEWSPAPER_PATH,
                            font_family=styles.TEXT_FONT_FAMILY,
                        ),
                        " will be where you can read articles on your favorite topics...",
                        font_family=styles.TEXT_FONT_FAMILY,
                    ),
                ),
                rx.hstack(
                    list_circle("3"),
                    rx.text(
                        "Interested in a specific news topic? ",
                        rx.link(
                            "Suggest one here...",
                            href=NEWS_TOPICS_PATH,
                            font_family=styles.TEXT_FONT_FAMILY,
                        ),
                        font_family=styles.TEXT_FONT_FAMILY,
                    ),
                ),
                rx.hstack(
                    list_circle("4"),
                    rx.text(
                        rx.link(
                            "Request a feature or give us any feedback",
                            href=CONTACT_URL,
                            font_family=styles.TEXT_FONT_FAMILY,
                            is_external=True,
                        ),
                        " you may have (yes, especially the negative ones)...",
                        font_family=styles.TEXT_FONT_FAMILY,
                    ),
                ),
                padding_top="50px",
                width="100%",
            ),
        ),
        margin_top="30px",
        margin_bottom="10px",
    )


@webpage(path=INDEX_PATH, title=TITLE.format(page_name="Home"), props={"min_height": "100%"})
def index() -> rx.Component:
    """Get the main The Daily Bite landing page."""
    return rx.cond(
        IndexState.logged_in,
        rx.flex(
            landing(),
            width="100%",
            min_height="100%",
            flex_direction="column",
            margin_bottom="4em",
            display="flex",
            flex="1",
        ),
    )
