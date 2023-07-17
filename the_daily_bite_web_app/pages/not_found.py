import reflex as rx

from the_daily_bite_web_app import styles
from the_daily_bite_web_app.components.logo import logo
from the_daily_bite_web_app.constants import INDEX_PATH


def not_found():
    return rx.center(
        rx.vstack(
            rx.heading("Oops! Page not found!", level=1),
            logo(
                width=["4.28em", "4.28em", "5.35em"],
                height=["4em", "4em", "5em"],
            ),
            rx.button(rx.link("Back to Home", href=INDEX_PATH)),
        ),
        width="100%",
        padding_y=["6em", "6em", "10em", "12em", "12em"],
        align_items="center",
    )
