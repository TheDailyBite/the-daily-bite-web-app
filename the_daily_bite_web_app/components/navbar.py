"""UI and logic for the navbar component."""

import pynecone as pc

from the_daily_bite_web_app import constants, styles
from the_daily_bite_web_app.components.logo import logo
from the_daily_bite_web_app.components.sidebar import sidebar as sb
from the_daily_bite_web_app.pages.index import index
from the_daily_bite_web_app.pages.news import news_topics, news_topics_subscribe
from the_daily_bite_web_app.states import NavbarState

try:
    from the_daily_bite_web_app.tsclient import client
except ImportError:
    client = None


# Styles to use for the navbar.
logo_style = {
    "width": "3.21em",
    "height": "3em",
}
logo = logo(**logo_style)

button_style = {
    "color": styles.DOC_REG_TEXT_COLOR,
    "_hover": {"color": styles.ACCENT_COLOR, "text_decoration": "none"},
}


def navbar(sidebar: pc.Component = None) -> pc.Component:
    """Create the navbar component.

    Args:
        sidebar: The sidebar component to use.
    """
    # If the sidebar is not provided, create a default one.
    sidebar = sidebar or sb()

    # Create the navbar component.
    return pc.box(
        pc.hstack(
            pc.link(
                pc.hstack(
                    logo,
                    pc.tablet_and_desktop(
                        pc.text(
                            "The Daily Bite",
                            font_size=styles.H3_FONT_SIZE,
                            font_weight=600,
                        ),
                    ),
                    spacing="0.25em",
                ),
                href=index.path,
                _hover={"text_decoration": "none"},
            ),
            pc.hstack(
                pc.tablet_and_desktop(
                    pc.link(
                        pc.text(
                            "News Topics",
                        ),
                        href=news_topics.path,
                        **button_style,
                    ),
                ),
                pc.tablet_and_desktop(
                    pc.link(
                        pc.text(
                            "Subscribe to News Topics",
                        ),
                        href=news_topics_subscribe.path,
                        **button_style,
                    ),
                ),
                pc.mobile_and_tablet(
                    pc.icon(
                        tag="hamburger",
                        on_click=NavbarState.toggle_sidebar,
                        width="1.5em",
                        height="1.5em",
                        _hover={
                            "cursor": "pointer",
                            "color": styles.ACCENT_COLOR,
                        },
                    ),
                ),
                spacing="1em",
            ),
            pc.drawer(
                pc.drawer_overlay(
                    pc.drawer_content(
                        pc.hstack(
                            logo,
                            pc.icon(
                                tag="close",
                                on_click=NavbarState.toggle_sidebar,
                                width="4em",
                                _hover={
                                    "cursor": "pointer",
                                    "color": styles.ACCENT_COLOR,
                                },
                            ),
                            justify="space-between",
                            margin_bottom="1.5em",
                        ),
                        sidebar if sidebar is not None else pc.text("Sidebar"),
                        padding_x="2em",
                        padding_top="2em",
                        bg="rgba(255,255,255, 0.97)",
                    ),
                    bg="rgba(255,255,255, 0.5)",
                ),
                placement="left",
                is_open=NavbarState.sidebar_open,
                on_close=NavbarState.toggle_sidebar,
                bg="rgba(255,255,255, 0.5)",
            ),
            justify="space-between",
            padding_x=styles.PADDING_X,
        ),
        bg="rgba(255,255,255, 0.9)",
        backdrop_filter="blur(10px)",
        padding_y=["0.8em", "0.8em", "0.5em"],
        border_bottom="0.05em solid rgba(100, 116, 139, .2)",
        position="sticky",
        width="100%",
        top="0px",
        z_index="99",
    )
