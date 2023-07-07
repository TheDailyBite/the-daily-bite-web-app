"""The main the daily bite website."""

import reflex as rx

from the_daily_bite_web_app import styles
from the_daily_bite_web_app.constants import (
    INDEX_PATH,
    LOGIN_PATH,
    NEWS_TOPICS_PATH,
    NEWSPAPER_PATH,
)
from the_daily_bite_web_app.middleware import CloseSidebarMiddleware
from the_daily_bite_web_app.pages import index, login, news_topics, newspaper
from the_daily_bite_web_app.states import BaseState, NewspaperState, NewsTopicsState

on_load_all_pages = [BaseState.verify_login]

# Create the app.
app = rx.App(
    state=BaseState,  # TODO ?
    style=styles.BASE_STYLE,
    stylesheets=styles.STYLESHEETS,
)

app.add_page(
    login,
    route=LOGIN_PATH,
    description="Read informative, well organized news, in easily digestible bites.",
    image="logo.png",
)

app.add_page(
    news_topics.component,
    route=news_topics.path,
    title=news_topics.title,
    description="Read informative, well organized news, in easily digestible bites.",
    image="logo.png",
    on_load=[*on_load_all_pages, NewsTopicsState.on_load],  # TODO - add on_load
)

app.add_page(
    newspaper.component,
    route=newspaper.path,
    title=newspaper.title,
    description="Read informative, well organized news, in easily digestible bites.",
    image="logo.png",
    on_load=[*on_load_all_pages, NewspaperState.on_load_newspaper],  # TODO - add on_load
)

app.add_page(
    index.component,
    route=index.path,
    title=index.title,
    description="Read informative, well organized news, in easily digestible bites.",
    image="logo.png",
    on_load=[*on_load_all_pages],
)


app.add_middleware(CloseSidebarMiddleware(), index=0)

# Run the app.
app.compile()
