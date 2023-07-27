"""Logic for the sidebar component."""

from __future__ import annotations

from typing import List, Optional

import inspect

import reflex as rx
from reflex.base import Base

from the_daily_bite_web_app import styles
from the_daily_bite_web_app.constants import DEFAULT_TITLE_SUFFIX
from the_daily_bite_web_app.route import Route

# Sidebar styles.
heading_style = {
    "color": styles.DOC_REG_TEXT_COLOR,
    "font_weight": "500",
}
heading_style2 = {
    "font_size": styles.TEXT_FONT_SIZE,
    "color": styles.DOC_REG_TEXT_COLOR,
    "font_weight": "500",
}
heading_style3 = {
    "font_weight": styles.DOC_SECTION_FONT_WEIGHT,
    "font_size": styles.H3_FONT_SIZE,
    "color": styles.DOC_HEADER_COLOR,
    "margin_bottom": "0.5em",
    "margin_left": "1.1em",
}


class SidebarItem(Base):
    """A single item in the sidebar."""

    # The name to display in the sidebar.
    names: str = ""

    # The link to navigate to when the item is clicked.
    link: str = ""

    # The children items.
    children: List[SidebarItem] = []


def create_item(route: Route, children=None):
    """Create a sidebar item from a route."""
    if children is None:
        name = route.title.split(DEFAULT_TITLE_SUFFIX)[0]
        return SidebarItem(names=name, link=route.path)
    return SidebarItem(
        names=inspect.getmodule(route).__name__.split(".")[-1].replace("_", " ").title(),
        children=list(map(create_item, children)),
    )


def get_sidebar_items_news():
    from the_daily_bite_web_app.pages import news

    items = [create_item(news.news_topics), create_item(news.newspaper)]
    return items


@rx.memo
def sidebar_leaf(
    item: SidebarItem,
    url: str,
) -> rx.Component:
    """Get the leaf node of the sidebar."""
    return rx.accordion_item(
        rx.cond(
            item.link == url,
            rx.link(
                item.names,
                href=item.link,
                color=styles.ACCENT_COLOR,
                _hover={"color": styles.ACCENT_COLOR},
            ),
            rx.link(
                item.names,
                href=item.link,
                color=styles.DOC_REG_TEXT_COLOR,
                _hover={"color": styles.ACCENT_COLOR},
            ),
        ),
        padding_left="1em",
        border="none",
    )


@rx.memo
def sidebar_item_comp(
    item: SidebarItem,
    index: List[int],
    url: str,
    first: bool,
):
    return rx.fragment(
        rx.cond(
            item.children.length() == 0,
            sidebar_leaf(item=item, url=url),
            rx.accordion_item(
                rx.cond(
                    first,
                    rx.accordion_button(
                        rx.accordion_icon(),
                        rx.text(
                            item.names,
                            font_size="1em",
                        ),
                        padding_y="0.5em",
                        _hover={
                            "color": styles.ACCENT_COLOR,
                        },
                    ),
                    rx.accordion_button(
                        rx.accordion_icon(),
                        rx.text(
                            item.names,
                            font_size="1em",
                        ),
                        padding_y="0.2em",
                        _hover={
                            "color": styles.ACCENT_COLOR,
                        },
                    ),
                ),
                rx.accordion_panel(
                    rx.accordion(
                        rx.vstack(
                            rx.foreach(
                                item.children,
                                lambda child: sidebar_item_comp(
                                    item=child,
                                    index=index,
                                    url=url,
                                    first=False,
                                ),
                            ),
                            align_items="start",
                            border_left="1px solid #e0e0e0",
                        ),
                        allow_multiple=True,
                        default_index=rx.cond(index, index[1:2], []),
                    ),
                    margin_left="1em",
                ),
                border="none",
            ),
        )
    )


def calculate_index(sidebar_items, url):
    if not isinstance(sidebar_items, list):
        sidebar_items = [sidebar_items]

    sub = 0
    for i, item in enumerate(sidebar_items):
        if len(item.children) == 0:
            sub += 1
        if item.link == url:
            return [i - sub]
        index = calculate_index(item.children, url)
        if index is not None:
            return [i - sub] + index
    return None


news = get_sidebar_items_news()


def get_prev_next(url):
    """Get the previous and next links in the sidebar."""
    sidebar_items = news  # + <others>
    # Flatten the list of sidebar items
    flat_items = []

    def append_to_items(items):
        for item in items:
            if len(item.children) == 0:
                flat_items.append(item)
            append_to_items(item.children)

    append_to_items(sidebar_items)
    for i, item in enumerate(flat_items):
        if item.link == url:
            if i == 0:
                return None, flat_items[i + 1]
            elif i == len(flat_items) - 1:
                return flat_items[i - 1], None
            else:
                return flat_items[i - 1], flat_items[i + 1]
    return None, None


@rx.memo
def sidebar_comp(
    url: str,
    news_index: List[int],
):
    return rx.box(
        rx.accordion(
            *[
                sidebar_item_comp(
                    item=item,
                    index=[-1],
                    url=url,
                    first=True,
                )
                for item in news
            ],
            allow_multiple=True,
            default_index=news_index,
        ),
        rx.divider(
            margin_bottom="1em",
            margin_top="0.5em",
        ),
        align_items="start",
        overflow_y="scroll",
        max_height="90%",
        padding_bottom="6em",
        padding_right="4em",
        position="fixed",
        scroll_padding="4em",
    )


def sidebar(url=None) -> rx.Component:
    """Render the sidebar."""
    news_index = calculate_index(news, url)
    # others
    return rx.box(
        sidebar_comp(
            url=url,
            news_index=news_index,
            # others
        ),
    )
