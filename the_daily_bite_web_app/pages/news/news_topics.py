import reflex as rx

from the_daily_bite_web_app import constants, styles
from the_daily_bite_web_app.constants import NEWS_TOPICS_PATH, TITLE
from the_daily_bite_web_app.states import NewsTopicsState
from the_daily_bite_web_app.states.models import NewsTopic
from the_daily_bite_web_app.templates import webpage


def to_ui_news_topic(news_topic: NewsTopicsState, idx: int):
    selected_background_color = "#756aee59"
    not_selected_background_color = "#fff"
    return rx.box(
        rx.cond(
            news_topic.is_user_subscribed == True,
            rx.cond(
                news_topic.is_selected == True,
                rx.icon(tag="check_circle", color="#fff"),
                rx.icon(tag="check_circle", color="#666"),
            ),  # is_user_subscribed
            rx.cond(
                news_topic.is_selected == True,
                rx.icon(tag="check_circle", color="#666"),
                rx.icon(tag="check_circle", color="#00000000"),
            ),  # not is_user_subscribed
        ),
        rx.vstack(
            rx.text(news_topic.topic),
            rx.box(
                rx.text("last publishing date: " + news_topic.last_publishing_date),
                display="flex",
                font_size="0.8rem",
                color="#666",
            ),
            spacing="0.3rem",
            align_items="center",
        ),
        background_color=rx.cond(
            news_topic.is_selected == True, selected_background_color, not_selected_background_color
        ),
        padding="1rem",
        border_radius="30px",
        border="1px solid #ddd",
        on_click=NewsTopicsState.toggle_news_topic_selected(idx),
        _hover={"bg": selected_background_color},
    )


@webpage(path=NEWS_TOPICS_PATH, title=TITLE.format(page_name="News Topics"))
def news_topics() -> rx.Component:
    """Get the news topics page."""
    return rx.cond(
        NewsTopicsState.logged_in,
        rx.container(
            rx.text(
                "Subscribe to your favorite News Topics to begin reading its published articles.",
                font_size="30px",
                text_align="center",
                background_image=styles.LINEAR_GRADIENT_TEXT_BACKGROUND,
                background_clip="text",
                text_fill_color="transparent",
                background_size="100%",
                background_color="#f3ec78",
            ),
            rx.cond(
                NewsTopicsState.is_refreshing_news_topics == True,
                rx.center(rx.circular_progress(is_indeterminate=True, size="100px")),
                rx.vstack(
                    rx.foreach(
                        NewsTopicsState.news_topics,
                        lambda news_topic, idx: to_ui_news_topic(news_topic, idx),
                    ),
                    margin_top="2rem",
                    spacing="1rem",
                    align_items="left",
                ),
            ),
            rx.center(
                rx.cond(
                    NewsTopicsState.is_updating_user_news_topic_subscriptions == True,
                    rx.circular_progress(is_indeterminate=True, size="100px"),
                    rx.button(
                        "Update",
                        display="flex",
                        width="250px",
                        height="80px",
                        flex_direction="colum",
                        justify_content="center",
                        flex_shrink="0",
                        color="#FFF",
                        text_align="center",
                        font_size="30px",
                        font_weight="600",
                        border_radius="30px",
                        background=styles.LINEAR_GRADIENT_BUTTON_BACKGROUND,
                        on_click=[
                            NewsTopicsState.update_user_news_topic_subscriptions,
                            NewsTopicsState.refresh_user_news_topics,
                        ],
                    ),
                ),
                margin_top="2rem",
            ),
            padding="2rem",
            max_width="600px",
            border="1px solid #ddd",
            border_radius="30px",
            margin_top="2rem",
            margin_bottom="2rem",
        ),
    )
