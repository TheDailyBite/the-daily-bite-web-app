import reflex as rx

from the_daily_bite_web_app import constants, styles
from the_daily_bite_web_app.constants import NEWSLETTER_PATH, TITLE
from the_daily_bite_web_app.states import NewsletterState
from the_daily_bite_web_app.templates import webpage


def newsletter_interest() -> rx.Component:
    return rx.center(
        rx.cond(
            NewsletterState.newsletter_interest_signed_up,
            rx.text(
                "Thank you for signing up!",
                font_size=styles.H1_FONT_SIZE,
                font_family=styles.TEXT_FONT_FAMILY,
                background_image=styles.LINEAR_GRADIENT_TEXT_BACKGROUND,
                background_clip="text",
            ),
            rx.box(
                rx.text(
                    "Join the Newsletter Waitlist",
                    font_size=styles.H1_FONT_SIZE,
                    font_family=styles.TEXT_FONT_FAMILY,
                    background_clip="text",
                    background_image=styles.LINEAR_GRADIENT_TEXT_BACKGROUND,
                ),
                rx.text(
                    "The newsletter will allow you to get the latest news on your favorite topics, in a bite sized format, straight to your inbox with the frequency you'd like.",
                    font_size=styles.H3_FONT_SIZE,
                    font_family=styles.TEXT_FONT_FAMILY,
                ),
                rx.divider(),
                rx.text(
                    "We will be in touch as soon as it is ready to be tested :)",
                    font_size=styles.H4_FONT_SIZE,
                    font_family=styles.TEXT_FONT_FAMILY,
                ),
                rx.wrap(
                    rx.input_group(
                        rx.input(
                            placeholder="Your email address...",
                            on_blur=NewsletterState.set_email,
                            type="email",
                        ),
                    ),
                    rx.button(
                        "Join Newsletter Waitlist",
                        on_click=NewsletterState.newsletter_interest_signup,
                        style=styles.BUTTON_LIGHT_NO_BACKGROUND,
                    ),
                    justify="left",
                    should_wrap_children=True,
                    spacing="1em",
                    padding_x=".25em",
                    padding_y="1em",
                ),
            ),
        )
    )


@webpage(
    path=NEWSLETTER_PATH, title=TITLE.format(page_name="Newsletter"), props={"min_height": "100%"}
)
def newsletter() -> rx.Component:
    return rx.cond(
        NewsletterState.logged_in,
        rx.container(
            newsletter_interest(),
            margin_top="2em",
            margin_bottom="2em",
        ),
    )
