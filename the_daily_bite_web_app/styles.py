"""App styling."""

import reflex as rx

# General styles.
BOLD_WEIGHT = "800"
NAVBAR_LOGO = "/navbar_logo.png"
LOGO_URL = "/logo.png"

PADDING_X = ["1em", "2em", "5em"]
PADDING_X2 = ["1em", "2em", "10em"]
HERO_FONT_SIZE = ["2em", "3em", "3em", "4em"]
H1_FONT_SIZE = ["2.2em", "2.4em", "2.5em"]
H2_FONT_SIZE = ["1.8em", "1.9em", "2em"]
H3_FONT_SIZE = "1.35em"
H4_FONT_SIZE = "1.1em"
TEXT_FONT_SIZE = "1em"
TEXT_FONT_FAMILY = "Raleway"
ACCENT_COLOR = "rgb(107,99,246)"
ACCENT_COLOR_LIGHT = "rgba(107,99,246, 0.4)"
ACCENT_COLOR_DARK = "rgb(86, 77, 209)"
SUBHEADING_COLOR = "rgb(37,50,56)"
LINEAR_GRADIENT_TEXT_BACKGROUND = "linear-gradient(271.68deg, #EE756A 25%, #756AEE 50%)"
LINEAR_GRADIENT_BUTTON_BACKGROUND = "linear-gradient(90deg, #756AEE 0%, #EE756A 100%)"
LIGHT_TEXT_COLOR = "#94a3b8"
LINK_STYLE = {
    "color": ACCENT_COLOR,
    "text_decoration": "none",
}
BUTTON_LIGHT_NO_BACKGROUND = {
    "border_radius": "6px",
    "box_shadow": "0px 0px 0px 1px rgba(84, 82, 95, 0.14), 0px 1px 2px rgba(31, 25, 68, 0.14);",
    "bg": "#FFFFFF",
    "padding_x": ".75em",
    "border_radius": "8px",
    "_hover": {
        "box_shadow": "0px 0px 0px 2px rgba(149, 128, 247, 0.60), 0px 2px 3px 0px rgba(3, 3, 11, 0.01), 0px 1px 2px 0px rgba(84, 82, 95, 0.12), 0px 0px 0px 1px rgba(32, 17, 126, 0.40) inset;",
    },
}

BUTTON_LIGHT_SELECTED = {
    "border_radius": "6px",
    "box_shadow": "0px 0px 0px 1px rgba(84, 82, 95, 0.14), 0px 1px 2px rgba(31, 25, 68, 0.14);",
    "bg": "#D3D3D3",
    "padding_x": ".75em",
    "border_radius": "8px",
    "_hover": {
        "box_shadow": "0px 0px 0px 2px rgba(149, 128, 247, 0.60), 0px 2px 3px 0px rgba(3, 3, 11, 0.01), 0px 1px 2px 0px rgba(84, 82, 95, 0.12), 0px 0px 0px 1px rgba(32, 17, 126, 0.40) inset;",
    },
}


# Doc page styles.
DOC_HEADER_COLOR = "#000000"
DOC_TEXT_COLOR = "#000000"
DOC_REG_TEXT_COLOR = "#666666"
DOC_LIGHT_TEXT_COLOR = "#999999"
DOCPAGE_BACKGROUND_COLOR = "#fafafa"

DOC_HEADING_FONT_WEIGHT = "900"
DOC_SUBHEADING_FONT_WEIGHT = "800"
DOC_SECTION_FONT_WEIGHT = "600"

DOC_SHADOW = "rgba(0, 0, 0, 0.15) 0px 2px 8px"
DOC_SHADOW_DARK = "rgba(0, 0, 0, 0.3) 0px 2px 8px"
DOC_SHADOW_LIGHT = "rgba(0, 0, 0, 0.08) 0px 4px 12px"

DOC_BORDER_RADIUS = "1em"

# The base application style.
BASE_STYLE = {
    "font_family": TEXT_FONT_FAMILY,
    "font_size": TEXT_FONT_SIZE,
    "::selection": {
        "background_color": ACCENT_COLOR_LIGHT,
    },
    rx.Text: {"font_family": TEXT_FONT_FAMILY, "font_size": TEXT_FONT_SIZE},
    rx.Markdown: {"font_family": TEXT_FONT_FAMILY, "font_size": TEXT_FONT_SIZE},
    rx.Heading: {"font_family": TEXT_FONT_FAMILY},
    rx.Divider: {"margin_bottom": "1em", "margin_top": "0.5em"},
    rx.Link: {"font_family": TEXT_FONT_FAMILY, "font_size": TEXT_FONT_SIZE},
}

# Fonts to include.
STYLESHEETS = [
    "https://fonts.googleapis.com/css2?family=Raleway:ital,wght@0,100;0,200;0,300;0,400;0,500;0,600;0,700;0,800;0,900;1,100;1,200;1,300;1,400;1,500;1,600;1,700;1,800;1,900&display=swap",
]
