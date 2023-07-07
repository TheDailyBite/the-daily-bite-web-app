import reflex as rx

from the_daily_bite_web_app import styles
from the_daily_bite_web_app.components.logo import logo
from the_daily_bite_web_app.constants import LOGIN_PATH
from the_daily_bite_web_app.states import LoginState


def login():
    return rx.center(
        rx.vstack(
            logo(
                width=["4.28em", "4.28em", "5.35em"],
                height=["4em", "4em", "5em"],
            ),
            rx.input(
                placeholder="User Id",
                margin_bottom="2em",
                margin_top="2em",
                text_align="center",
                on_change=LoginState.set_user_id_field,
            ),
            rx.button("Log in", on_click=LoginState.log_in),
        ),
        width="100%",
        padding_y=["6em", "6em", "10em", "12em", "12em"],
        align_items="center",
    )
