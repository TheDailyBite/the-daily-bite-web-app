import reflex as rx

from the_daily_bite_web_app import constants, styles
from the_daily_bite_web_app.components.logo import logo
from the_daily_bite_web_app.pages.index import index
from the_daily_bite_web_app.states import BaseState

footer_item_style = {
    "font_weight": "500",
    "_hover": {"color": styles.ACCENT_COLOR},
}

footer_style = {}


def footer(style=footer_style):
    return rx.cond(
        BaseState.logged_in,
        rx.box(
            rx.hstack(
                rx.vstack(
                    rx.hstack(
                        logo(
                            width=["72px"],
                            height=["72px"],
                        ),
                        rx.text(
                            "Copyright © 2023 The Daily Bite",
                            font_weight="500",
                            color=styles.LIGHT_TEXT_COLOR,
                            padding_left="0.5em",
                        ),
                        align_items="center",
                        margin_bottom="0.5em",
                    ),
                    align_items="start",
                ),
                rx.hstack(
                    rx.vstack(
                        rx.text("Welcome to The Daily Bite,", color=styles.SUBHEADING_COLOR),
                        rx.text(BaseState.user_name, color=styles.SUBHEADING_COLOR),
                        rx.cond(
                            BaseState.logged_in == True,
                            rx.link("Log Out", on_click=BaseState.log_out),
                        ),
                        align_items="start",
                        margin_right="2em",
                    ),
                    rx.vstack(
                        rx.text("Resources", color=styles.SUBHEADING_COLOR),
                        rx.link(
                            "Threads",
                            href=constants.THREADS_URL,
                            style=footer_item_style,
                            is_external=True,
                        ),
                        rx.link(
                            "Contact",
                            href=constants.CONTACT_URL,
                            style=footer_item_style,
                            is_external=True,
                        ),
                        align_items="start",
                    ),
                    align_items="start",
                ),
                justify_content="space-between",
                align_items="start",
            ),
            color=styles.LIGHT_TEXT_COLOR,
            bg="rgba(255,255,255, 0.9)",
            backdrop_filter="blur(10px)",
            padding_y=["0.8em", "0.8em", "0.5em"],
            border_top="0.05em solid rgba(100, 116, 139, .2)",
            position="sticky",
            padding_x=styles.PADDING_X,
            width="100%",
            bottom="0",
            z_index="99",
            height="100px",
            **style,
        ),
    )
