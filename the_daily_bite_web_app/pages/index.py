import pynecone as pc

from the_daily_bite_web_app import constants, styles
from the_daily_bite_web_app.constants import INDEX_PATH
from the_daily_bite_web_app.states import IndexState
from the_daily_bite_web_app.templates import webpage


def landing():
    return pc.container(
        pc.vstack(
            pc.box(
                pc.text(
                    "News. Daily. Bite Sized.",
                    font_size=styles.HERO_FONT_SIZE,
                    font_weight=700,
                    font_family=styles.TEXT_FONT_FAMILY,
                ),
                pc.text(
                    "Find your favorite news topics, or suggest a new one for us to track.",
                    font_size=styles.HERO_FONT_SIZE,
                    font_weight=800,
                    font_family=styles.TEXT_FONT_FAMILY,
                    background_image="linear-gradient(271.68deg, #EE756A 25%, #756AEE 50%)",
                    background_clip="text",
                ),
                text_align="center",
                line_height="1.15",
            ),
            pc.container(
                "Read informative news on the daily, in a reasonable amount of time!",
                color="grey",
                font_size="1.1em",
                font_family=styles.TEXT_FONT_FAMILY,
                text_align="center",
            ),
        )
    )


def c2a():
    return pc.box(
        pc.button_group(
            pc.button(
                pc.link(
                    pc.box(
                        "Read the News Daily",
                        pc.icon(
                            tag="star",
                            color="#eec600",
                            margin_left="0.2em",
                            margin_bottom="0.2em",
                        ),
                        width="100%",
                        height="100%",
                    ),
                    href=constants.TWITTER_URL,
                    _hover={},
                ),
                bg=styles.ACCENT_COLOR,
                color="white",
                border_color=styles.ACCENT_COLOR_DARK,
                _hover={"bg": styles.ACCENT_COLOR_DARK},
            ),
            pc.button(
                pc.icon(tag="close", color="white", height=".5em", width=".5em"),
                on_click=IndexState.close_c2a,
                bg=styles.ACCENT_COLOR,
                color="white",
                _hover={"bg": styles.ACCENT_COLOR_DARK},
            ),
            opacity="0.95",
            backdrop_filter="blur(6px)",
            is_attached=True,
            variant="outline",
            box_shadow="xl",
        ),
        z_index="50",
        display="flex",
        justify_content="center",
        position="fixed",
        bottom="2em",
        left="0",
        right="0",
    )


@webpage(path=INDEX_PATH)
def index() -> pc.Component:
    """Get the main The Daily Bite landing page."""
    return pc.box(
        landing(),
        pc.cond(
            IndexState.show_c2a,
            c2a(),
        ),
        # background_image="/grid.png",
        # background_repeat="no-repeat",
        # background_position="top",
        # width="100%",
    )