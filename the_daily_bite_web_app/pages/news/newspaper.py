import pynecone as pc

from the_daily_bite_web_app import constants, styles
from the_daily_bite_web_app.constants import NEWSPAPER_PATH
from the_daily_bite_web_app.states.models import ArticleSummarizationLength, NewspaperTopic
from the_daily_bite_web_app.states.newspaper import NewspaperState, NewsTopicsState
from the_daily_bite_web_app.templates import webpage


def to_ui_article_lengths_button(
    article_summarization_length: ArticleSummarizationLength, idx: int
):
    selected_background_color = "#756aee59"
    not_selected_background_color = "#fff"
    return pc.button(
        article_summarization_length.summarization_length,
        background_color=pc.cond(
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
    return pc.button(
        newspaper_topic.topic,
        background_color=pc.cond(
            newspaper_topic.is_selected, selected_background_color, not_selected_background_color
        ),
        padding="1rem",
        border="1px solid #ddd",
        width="80%",
        # on_click=NewspaperState.article_summarization_length_selected(idx),
        _hover={"bg": selected_background_color},
    )


@webpage(path=NEWSPAPER_PATH)
def newspaper() -> pc.Component:
    """Get the news topics page."""
    return pc.vstack(
        pc.box(
            pc.text(
                "Article Length",
                font_size="22px",
                font_style="italic",
                font_weight="600",
                text_align="center",
                margin_top="1rem",
                text_color="#000",
            ),
            pc.divider(),
            pc.vstack(
                pc.foreach(
                    NewspaperState.article_summarization_lengths,
                    lambda article_summarization_length, idx: to_ui_article_lengths_button(
                        article_summarization_length, idx
                    ),
                ),
                margin_top="2rem",
                margin_bottom="2rem",
                spacing="1rem",
                align_items="center",
            ),
            width="100%",
            border_radius="1rem",
            background_color="#fff",
            margin_left="4rem",
            box_shadow="0px 4px 4px 0px rgba(0, 0, 0, 0.25) inset, 0px 4px 4px 0px rgba(0, 0, 0, 0.25)",
        ),
        pc.box(
            pc.text(
                "News Topics",
                font_size="22px",
                font_style="italic",
                font_weight="600",
                text_align="center",
                margin_top="1rem",
                text_color="#000",
            ),
            pc.divider(),
            pc.vstack(
                pc.foreach(
                    NewspaperState.get_newspaper_topics,
                    lambda newspaper_topic, idx: to_ui_newspaper_topic_button(newspaper_topic, idx),
                ),
                margin_top="2rem",
                margin_bottom="2rem",
                spacing="1rem",
                align_items="center",
            ),
            width="100%",
            border_radius="1rem",
            background_color="#fff",
            margin_left="4rem",
            box_shadow="0px 4px 4px 0px rgba(0, 0, 0, 0.25) inset, 0px 4px 4px 0px rgba(0, 0, 0, 0.25)",
        ),
        width="20%",
        margin_top="2rem",
        margin_bottom="2rem",
    )
