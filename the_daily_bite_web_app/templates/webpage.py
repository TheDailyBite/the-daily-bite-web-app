from typing import Callable

import reflex as rx

from the_daily_bite_web_app.route import Route


def webpage(path: str, title: str, props=None) -> Callable:
    """A template that most pages on the thedailybite.io site should use.

    This template wraps the webpage with the navbar and footer.

    Args:
        path: The path of the page.
        title: The title of the page.
        props: Props to apply to the template.

    Returns:
        A wrapper function that returns the full webpage.
    """
    props = props or {}
    if not title:
        raise ValueError("Title must be provided.")

    def webpage(contents: Callable[[], Route]) -> Route:
        """Wrapper to create a templated route.

        Args:
            contents: The function to create the page route.

        Returns:
            The templated route.
        """

        def wrapper(*children, **props) -> rx.Component:
            """The template component.

            Args:
                children: The children components.
                props: The props to apply to the component.

            Returns:
                The component with the template applied.
            """
            # Import here to avoid circular imports.
            from the_daily_bite_web_app.components.footer import footer
            from the_daily_bite_web_app.components.navbar import navbar

            # Wrap the component in the template.
            return rx.box(navbar(), contents(*children, **props), footer(), **props)

        return Route(
            path=path,
            title=title,
            component=wrapper,
        )

    return webpage
