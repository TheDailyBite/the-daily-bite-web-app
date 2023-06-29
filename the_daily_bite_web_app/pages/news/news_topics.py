import pynecone as pc

from the_daily_bite_web_app import constants, styles
from the_daily_bite_web_app.constants import NEWS_TOPICS_PATH
from the_daily_bite_web_app.states import NewsTopicsState
from the_daily_bite_web_app.states.models import NewsTopic
from the_daily_bite_web_app.templates import webpage


def to_ui_news_topic(news_topic: NewsTopicsState, idx: int):
    selected_background_color = "#756aee59"
    not_selected_background_color = "#fff"
    return pc.box(
        pc.cond(
            news_topic.is_user_subscribed,
            pc.cond(
                news_topic.is_selected,
                pc.icon(tag="check_circle", color="#fff"),
                pc.icon(tag="check_circle", color="#666"),
            ),  # is_user_subscribed
            pc.cond(
                news_topic.is_selected,
                pc.icon(tag="check_circle", color="#666"),
                pc.icon(tag="check_circle", color="#00000000"),
            ),  # not is_user_subscribed
        ),
        pc.vstack(
            pc.text(news_topic.topic),
            pc.box(
                pc.text(news_topic.category),
                pc.text(" · ", margin_x="0.3rem"),
                pc.text("last publishing date: " + news_topic.last_publishing_date),
                display="flex",
                font_size="0.8rem",
                color="#666",
            ),
            spacing="0.3rem",
            align_items="center",
        ),
        background_color=pc.cond(
            news_topic.is_selected, selected_background_color, not_selected_background_color
        ),
        padding="1rem",
        border_radius="30px",
        border="1px solid #ddd",
        on_click=NewsTopicsState.toggle_news_topic_selected(idx),
        _hover={"bg": selected_background_color},
    )


@webpage(path=NEWS_TOPICS_PATH)
def news_topics() -> pc.Component:
    """Get the news topics page."""
    return pc.container(
        pc.text(
            "Subscribe to your favorite News Topics to begin reading its published articles.",
            font_size="30px",
            text_align="center",
            background_image="linear-gradient(271.68deg, #EE756A 25%, #756AEE 50%)",
            background_clip="text",
            text_fill_color="transparent",
            background_size="100%",
            background_color="#f3ec78",
        ),
        pc.cond(
            NewsTopicsState.is_refreshing_news_topics,
            pc.center(pc.circular_progress(is_indeterminate=True, size="100px")),
            pc.vstack(
                pc.foreach(
                    NewsTopicsState.news_topics,
                    lambda news_topic, idx: to_ui_news_topic(news_topic, idx),
                ),
                margin_top="2rem",
                spacing="1rem",
                align_items="left",
            ),
        ),
        pc.center(
            pc.cond(
                NewsTopicsState.is_updating_user_news_topic_subscriptions,
                pc.circular_progress(is_indeterminate=True, size="100px"),
                pc.button(
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
                    background="linear-gradient(90deg, #756AEE 0%, #EE756A 100%)",
                    on_click=[
                        NewsTopicsState.updating_news_topic_subscriptions,
                        NewsTopicsState.update_user_news_topic_subscriptions,
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
    )
