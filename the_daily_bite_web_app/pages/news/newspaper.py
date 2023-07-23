from typing import Callable, List, Union

import reflex as rx
from news_aggregator_data_access_layer.constants import SummarizationLength

from the_daily_bite_web_app import constants, styles
from the_daily_bite_web_app.constants import NEWS_TOPICS_PATH, NEWSPAPER_PATH, TITLE
from the_daily_bite_web_app.states.models import (
    ArticleSummarizationLength,
    NewsArticle,
    NewspaperTopic,
)
from the_daily_bite_web_app.states.newspaper import NewspaperState
from the_daily_bite_web_app.templates import webpage


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
        margin_top="1em",
    )


def to_ui_article(newspaper_article: NewsArticle) -> rx.Component:
    title: str = newspaper_article.title
    published_dt: str = newspaper_article.published_on_dt
    return rx.box(
        rx.center(
            rx.text(title, font_size=styles.H2_FONT_SIZE, font_style="italic", font_weight="light")
        ),
        rx.divider(),
        rx.box(
            rx.cond(
                NewspaperState.get_selected_article_summarization_length.summarization_length
                == SummarizationLength.FULL.value,
                rx.html(newspaper_article.full_summary_text, element="p"),
            ),
            rx.cond(
                NewspaperState.get_selected_article_summarization_length.summarization_length
                == SummarizationLength.MEDIUM.value,
                rx.html(newspaper_article.medium_summary_text, element="p"),
            ),
            rx.cond(
                NewspaperState.get_selected_article_summarization_length.summarization_length
                == SummarizationLength.SHORT.value,
                rx.html(newspaper_article.short_summary_text, element="p"),
            ),
            padding="1em",
        ),
        rx.divider(),
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
            margin_top="1em",
        ),
        width="100%",
        shadow="md",
        border_width="1px",
        border_radius="lg",
        margin_top="2em",
        padding="1.5em",
    )


def topic_newspaper():
    return rx.box(
        rx.vstack(
            rx.text(
                "Bites on " + '"' + NewspaperState.get_selected_topic_name + '"',
                font_size=styles.H1_FONT_SIZE,
                background_image=styles.LINEAR_GRADIENT_TEXT_BACKGROUND,
                background_clip="text",
            ),
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
        justify="center",
    )


def option_menus():
    return rx.hstack(
        rx.menu(
            rx.menu_button(
                rx.hstack(
                    rx.text("Article Summarization Lengths"),
                    rx.icon(tag="chevron_down"),
                    cursor="pointer",
                )
            ),
            rx.menu_list(
                rx.foreach(
                    NewspaperState.article_summarization_lengths,
                    lambda article_summarization_length, idx: rx.link(
                        rx.menu_item(article_summarization_length.summarization_length),
                        on_click=NewspaperState.article_summarization_length_selected(idx),
                    ),
                ),
            ),
        ),
        rx.menu(
            rx.menu_button(
                rx.hstack(rx.text("Newspaper Topic"), rx.icon(tag="chevron_down"), cursor="pointer")
            ),
            rx.menu_list(
                rx.cond(
                    NewspaperState.has_subscribed_newspaper_topics == True,
                    rx.foreach(
                        NewspaperState.get_newspaper_topics,
                        lambda newspaper_topic, idx: rx.link(
                            rx.menu_item(newspaper_topic.topic),
                            on_click=NewspaperState.newspaper_topic_selected(idx),
                        ),
                    ),
                    rx.link(
                        rx.menu_item("Subscribe to News Topics here!"),
                        href=NEWS_TOPICS_PATH,
                    ),
                ),
            ),
        ),
        margin_bottom="1em",
        margin_top="0.5em",
    )


@webpage(path=NEWSPAPER_PATH, title=TITLE.format(page_name="Newspaper"))
def newspaper() -> rx.Component:
    """Get the news topics page."""
    return rx.vstack(
        rx.cond(
            NewspaperState.is_refreshing_newspaper_topics == False,
            option_menus(),
        ),
        rx.divider(),
        rx.hstack(
            rx.cond(
                NewspaperState.has_subscribed_newspaper_topics == True,
                topic_newspaper(),
            ),
        ),
        margin="1rem",
    )
