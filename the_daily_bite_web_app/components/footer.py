import pynecone as pc

from the_daily_bite_web_app import constants, styles
from the_daily_bite_web_app.components.logo import logo
from the_daily_bite_web_app.pages.index import index

footer_item_style = {
    "font_family": "Inter",
    "font_weight": "500",
    "_hover": {"color": styles.ACCENT_COLOR},
}

footer_style = {
    "box_shadow": "medium-lg",
    "border_top": "0.2em solid #F0F0F0",
    "vertical_align": "bottom",
    "padding_top": "4em",
    "padding_bottom": "2em",
    "padding_x": styles.PADDING_X2,
    "bg": "white",
}


def footer(style=footer_style):
    return pc.box(
        pc.vstack(
            pc.hstack(
                pc.desktop_only(
                    logo(
                        width=["4.28em", "4.28em", "5.35em"],
                        height=["4em", "4em", "5em"],
                    ),
                ),
                pc.vstack(
                    pc.text("Site", color=styles.SUBHEADING_COLOR),
                    pc.link("Home", href=index.path, style=footer_item_style),
                    align_items="start",
                ),
                pc.vstack(
                    pc.text("Resources", color=styles.SUBHEADING_COLOR),
                    pc.link(
                        "About",
                        href="/TODO",
                        style=footer_item_style,
                    ),
                    pc.link(
                        "Contact",
                        href=constants.CONTACT_URL,
                        style=footer_item_style,
                    ),
                    pc.link(
                        "Twitter",
                        href=constants.TWITTER_URL,
                        style=footer_item_style,
                    ),
                    align_items="start",
                ),
                justify="space-between",
                color=styles.LIGHT_TEXT_COLOR,
                align_items="top",
                padding_bottom="3em",
                min_width="100%",
            ),
            pc.hstack(
                pc.text(
                    "Copyright © 2023 The Daily Bite",
                    font_weight="500",
                ),
                justify="space-between",
                color=styles.LIGHT_TEXT_COLOR,
                padding_bottom="2em",
                min_width="100%",
            ),
        ),
        **style,
    )
