"""The main the daily bite website."""

import reflex as rx

from the_daily_bite_web_app import styles
from the_daily_bite_web_app.constants import (
    INDEX_PATH,
    LOGIN_PATH,
    NEWS_TOPICS_PATH,
    NEWSPAPER_PATH,
    TITLE,
)
from the_daily_bite_web_app.middleware import CloseSidebarMiddleware
from the_daily_bite_web_app.pages import index, login, news_topics, newsletter, newspaper, not_found
from the_daily_bite_web_app.states import BaseState, NewspaperState, NewsTopicsState

on_load_all_pages = [BaseState.verify_login]

# Create the app.
app = rx.App(
    style=styles.BASE_STYLE,
    stylesheets=styles.STYLESHEETS,
)

app.add_page(
    login,
    route=LOGIN_PATH,
    title=TITLE.format(page_name="Login"),
    description="Read informative, well organized news, in easily digestible bites.",
    image="logo.png",
)

app.add_page(
    news_topics.component,
    route=news_topics.path,
    title=news_topics.title,
    description="Read informative, well organized news, in easily digestible bites.",
    image="logo.png",
    on_load=[*on_load_all_pages, NewsTopicsState.on_load],
)

app.add_page(
    newspaper.component,
    route=newspaper.path,
    title=newspaper.title,
    description="Read informative, well organized news, in easily digestible bites.",
    image="logo.png",
    on_load=[*on_load_all_pages, NewspaperState.on_load_newspaper],
)

app.add_page(
    index.component,
    route=index.path,
    title=index.title,
    description="Read informative, well organized news, in easily digestible bites.",
    image="logo.png",
    on_load=[*on_load_all_pages],
)

app.add_page(
    newsletter.component,
    route=newsletter.path,
    title=newsletter.title,
    description="Read informative, well organized news, in easily digestible bites.",
    image="logo.png",
    on_load=[*on_load_all_pages],
)

app.add_custom_404_page(
    not_found,
    title=TITLE.format(page_name="404"),
)

app.add_middleware(CloseSidebarMiddleware(), index=0)

# Run the app.
app.compile()
