"""The main the daily bite website."""

import pynecone as pc

from the_daily_bite_web_app import styles
from the_daily_bite_web_app.base_state import State
from the_daily_bite_web_app.middleware import CloseSidebarMiddleware
from the_daily_bite_web_app.pages import routes

# Create the app.
app = pc.App(
    state=State,
    style=styles.BASE_STYLE,
    stylesheets=styles.STYLESHEETS,
)

# Add the pages to the app.
for route in routes:
    app.add_page(
        route.component,
        route.path,
        route.title,
        description="Read informative, well organized news, in easily digestible bites.",
        image="logo.png",
    )

# Add the middleware.
app.add_middleware(CloseSidebarMiddleware(), index=0)

# Add redirects
redirects = [
    # ("/docs", "/docs/getting-started/introduction"),
]

for source, target in redirects:
    app.add_page(pc.fragment(), route=source, on_load=pc.redirect(target))

# Run the app.
app.compile()
