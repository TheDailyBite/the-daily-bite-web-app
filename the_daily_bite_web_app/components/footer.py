import reflex as rx

from the_daily_bite_web_app import constants, styles
from the_daily_bite_web_app.components.logo import logo
from the_daily_bite_web_app.pages.index import index
from the_daily_bite_web_app.states import BaseState

footer_item_style = {
    "font_family": "Inter",
    "font_weight": "500",
    "_hover": {"color": styles.ACCENT_COLOR},
}

footer_style = {
    "box_shadow": "medium-lg",
    "border_top": "0.2em solid #F0F0F0",
    "vertical_align": "top",
    "padding_top": "0.5em",
    "padding_bottom": "0.5em",
    "padding_x": styles.PADDING_X2,
    "bg": "white",
}


def footer(style=footer_style):
    return rx.box(
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
                    rx.cond(BaseState.logged_in, rx.link("Log Out", on_click=BaseState.log_out)),
                    align_items="start",
                    margin_right="2em",
                ),
                rx.vstack(
                    rx.text("Resources", color=styles.SUBHEADING_COLOR),
                    rx.link(
                        "Threads",
                        href=constants.THREADS_URL,
                        style=footer_item_style,
                    ),
                    rx.link(
                        "Contact",
                        href=constants.CONTACT_URL,
                        style=footer_item_style,
                    ),
                    align_items="start",
                ),
                align_items="start",
            ),
            justify_content="space-between",
            align_items="start",
        ),
        color=styles.LIGHT_TEXT_COLOR,
        **style,
    )
