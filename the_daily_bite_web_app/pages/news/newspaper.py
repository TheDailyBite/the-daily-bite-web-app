from typing import Callable, List, Union

import reflex as rx
from news_aggregator_data_access_layer.constants import SummarizationLength

from the_daily_bite_web_app import constants, styles
from the_daily_bite_web_app.constants import NEWS_TOPICS_PATH, NEWSPAPER_PATH
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
            article_summarization_length.is_selected == True,
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
            newspaper_topic.is_selected == True,
            selected_background_color,
            not_selected_background_color,
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
        rx.heading(title),
        rx.box(
            rx.cond(
                NewspaperState.get_selected_article_summarization_length.summarization_length
                == SummarizationLength.FULL.value,
                rx.text(newspaper_article.full_summary_text),
            ),
            rx.cond(
                NewspaperState.get_selected_article_summarization_length.summarization_length
                == SummarizationLength.MEDIUM.value,
                rx.text(newspaper_article.medium_summary_text),
            ),
            rx.cond(
                NewspaperState.get_selected_article_summarization_length.summarization_length
                == SummarizationLength.SHORT.value,
                rx.text(newspaper_article.short_summary_text),
            ),
            padding="1rem",
            shadow="md",
            border_width="1px",
            border_radius="md",
        ),
        rx.hstack(
            rx.hstack(
                rx.foreach(
                    newspaper_article.source_urls,
                    lambda source_url, idx: rx.link(
                        "[" + idx + "]", href=source_url, is_external=True
                    ),
                ),
                spacing="0.25em",
            ),
            rx.text("Published at: " + published_dt),
            justify_content="space-between",
        ),
        width="100%",
        shadow="md",
        border_width="1px",
        border_radius="lg",
    )


def topic_newspaper():
    return rx.box(
        rx.vstack(
            rx.cond(
                NewspaperState.is_refreshing_newspaper == True,
                rx.circular_progress(is_indeterminate=True, size="100px"),
                rx.foreach(
                    NewspaperState.get_topic_newspaper_articles_published_dates,
                    lambda publishing_date, idx: to_ui_newspaper_date_section(publishing_date, idx),
                ),
            ),
            rx.cond(
                NewspaperState.is_refreshing_newspaper == False,
                rx.cond(
                    NewspaperState.is_loading_more_articles == True,
                    rx.circular_progress(is_indeterminate=True, size="100px"),
                    rx.button(
                        "Load More Articles",
                        on_click=[
                            NewspaperState.load_more_articles,
                        ],
                    ),
                ),
            ),
        ),
        width="100%",
        padding="1rem",
        shadow="md",
        border_width="1px",
        border_radius="md",
    )


@webpage(path=NEWSPAPER_PATH)
def newspaper() -> rx.Component:
    """Get the news topics page."""
    return rx.hstack(
        rx.cond(
            NewspaperState.has_subscribed_newspaper_topics == True,
            topic_newspaper(),
            rx.box(width="100%"),
        ),
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
                background_color="#fff",
                shadow="md",
                border_width="1px",
                border_radius="md",
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
                    NewspaperState.is_refreshing_newspaper_topics == True,
                    rx.center(rx.circular_progress(is_indeterminate=True, size="100px")),
                    rx.vstack(
                        rx.cond(
                            NewspaperState.has_subscribed_newspaper_topics == True,
                            rx.foreach(
                                NewspaperState.get_newspaper_topics,
                                lambda newspaper_topic, idx: to_ui_newspaper_topic_button(
                                    newspaper_topic, idx
                                ),
                            ),
                            rx.box(
                                rx.text(
                                    "You haven't subscribed to any news topics.",
                                    text_align="center",
                                ),
                                rx.link(
                                    rx.button("Subscribe to News Topics here!"),
                                    href=NEWS_TOPICS_PATH,
                                ),
                            ),
                        ),
                        spacing="1rem",
                        align_items="center",
                        margin_top="1rem",
                        margin_bottom="1rem",
                    ),
                ),
                width="100%",
                background_color="#fff",
                shadow="md",
                border_width="1px",
                border_radius="md",
            ),
            width="20%",
        ),
        margin="1rem",
    )
