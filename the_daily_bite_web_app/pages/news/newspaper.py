from typing import Callable, List, Union

import reflex as rx

from the_daily_bite_web_app import constants, styles
from the_daily_bite_web_app.constants import NEWSPAPER_PATH
from the_daily_bite_web_app.states.models import (
    ArticleSummarizationLength,
    NewsArticle,
    NewspaperTopic,
)
from the_daily_bite_web_app.states.newspaper import NewspaperState
from the_daily_bite_web_app.templates import webpage


def to_ui_article_lengths_button(
    article_summarization_length: ArticleSummarizationLength, idx: int
):
    selected_background_color = "#756aee59"
    not_selected_background_color = "#fff"
    return rx.button(
        article_summarization_length.summarization_length,
        background_color=rx.cond(
            article_summarization_length.is_selected,
            selected_background_color,
            not_selected_background_color,
        ),
        padding="1rem",
        border="1px solid #ddd",
        width="80%",
        on_click=NewspaperState.article_summarization_length_selected(idx),
        _hover={"bg": selected_background_color},
    )


def to_ui_newspaper_topic_button(newspaper_topic: NewspaperTopic, idx: int):
    selected_background_color = "#756aee59"
    not_selected_background_color = "#fff"
    return rx.button(
        newspaper_topic.topic,
        background_color=rx.cond(
            newspaper_topic.is_selected, selected_background_color, not_selected_background_color
        ),
        padding="1rem",
        border="1px solid #ddd",
        width="80%",
        on_click=NewspaperState.newspaper_topic_selected(idx),
        _hover={"bg": selected_background_color},
    )


def to_ui_newspaper_date_section(article_publishing_date: str, idx: int):
    articles: List[NewsArticle] = NewspaperState.get_topic_newspaper_articles_no_date[idx]
    return rx.box(
        rx.center(article_publishing_date, font_size="22px"),
        rx.divider(),
        rx.foreach(
            articles,
            to_ui_article,
        ),
        width="100%",
    )


def to_ui_article(newspaper_article: NewsArticle) -> rx.Component:
    title: str = newspaper_article.title
    published_dt: str = newspaper_article.published_on_dt
    return rx.box(
        rx.text(title),
        rx.box(
            rx.text(newspaper_article.full_summary_text),
            padding="1rem",
            border="1px solid #ddd",
        ),
        rx.hstack(
            rx.text("Sources: [1], [2], [3]"),
            rx.text(published_dt),
            justify_content="space-between",
        ),
        width="100%",
    )


def topic_newspaper():
    return rx.box(
        rx.vstack(
            rx.foreach(
                NewspaperState.get_topic_newspaper_articles_published_dates,
                lambda publishing_date, idx: to_ui_newspaper_date_section(publishing_date, idx),
            ),
        ),
        width="100%",
        padding="1rem",
        border="1px solid #ddd",
    )


@webpage(path=NEWSPAPER_PATH)
def newspaper() -> rx.Component:
    """Get the news topics page."""
    return rx.hstack(
        topic_newspaper(),
        rx.vstack(
            rx.box(
                rx.text(
                    "Article Length",
                    font_size="22px",
                    font_style="italic",
                    font_weight="600",
                    text_align="center",
                    margin_top="1rem",
                    text_color="#000",
                ),
                rx.divider(),
                rx.vstack(
                    rx.foreach(
                        NewspaperState.article_summarization_lengths,
                        lambda article_summarization_length, idx: to_ui_article_lengths_button(
                            article_summarization_length, idx
                        ),
                    ),
                    spacing="1rem",
                    align_items="center",
                    margin_top="1rem",
                    margin_bottom="1rem",
                ),
                width="100%",
                border_radius="1rem",
                background_color="#fff",
                box_shadow="0px 4px 4px 0px rgba(0, 0, 0, 0.25) inset, 0px 4px 4px 0px rgba(0, 0, 0, 0.25)",
            ),
            rx.box(
                rx.text(
                    "News Topics",
                    font_size="22px",
                    font_style="italic",
                    font_weight="600",
                    text_align="center",
                    margin_top="1rem",
                    text_color="#000",
                ),
                rx.divider(),
                rx.cond(
                    NewspaperState.is_refreshing_newspaper_topics,
                    rx.center(rx.circular_progress(is_indeterminate=True, size="100px")),
                    rx.vstack(
                        rx.foreach(
                            NewspaperState.get_newspaper_topics,
                            lambda newspaper_topic, idx: to_ui_newspaper_topic_button(
                                newspaper_topic, idx
                            ),
                        ),
                        spacing="1rem",
                        align_items="center",
                        margin_top="1rem",
                        margin_bottom="1rem",
                    ),
                ),
                width="100%",
                border_radius="1rem",
                background_color="#fff",
                box_shadow="0px 4px 4px 0px rgba(0, 0, 0, 0.25) inset, 0px 4px 4px 0px rgba(0, 0, 0, 0.25)",
            ),
            width="20%",
        ),
        margin="1rem",
    )
