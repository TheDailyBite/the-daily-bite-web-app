"""The Reflex logo component."""

import reflex as rx

from the_daily_bite_web_app import styles


def logo(**style_props):
    """Create a Reflex logo component.

    Args:
        style_props: The style properties to apply to the component.
    """
    return rx.image(
        src=styles.LOGO_URL,
        **style_props,
    )


def navbar_logo(**style_props):
    """Create a Reflex logo component.

    Args:
        style_props: The style properties to apply to the component.
    """
    return rx.image(
        src=styles.NAVBAR_LOGO,
        **style_props,
    )
