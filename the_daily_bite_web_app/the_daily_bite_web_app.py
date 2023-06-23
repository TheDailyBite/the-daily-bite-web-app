"""The main the daily bite website."""

import pynecone as pc

from the_daily_bite_web_app import styles
from the_daily_bite_web_app.constants import LOGIN_PATH
from the_daily_bite_web_app.middleware import CloseSidebarMiddleware
from the_daily_bite_web_app.pages import login, routes
from the_daily_bite_web_app.states import BaseState

# Create the app.
app = pc.App(
    state=BaseState,  # TODO ?
    style=styles.BASE_STYLE,
    stylesheets=styles.STYLESHEETS,
)

app.add_page(
    login,
    LOGIN_PATH,
    description="Read informative, well organized news, in easily digestible bites.",
    image="logo.png",
)

# Add the pages to the app.
for route in routes:
    app.add_page(
        route.component,
        route.path,
        route.title,
        description="Read informative, well organized news, in easily digestible bites.",
        image="logo.png",
        on_load=BaseState.verify_login(),
    )

# Add the middleware.
app.add_middleware(CloseSidebarMiddleware(), index=0)

# Run the app.
app.compile()
