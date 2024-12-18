"""Manage routing for the application."""


from typing import Callable, Union

import inspect

import reflex as rx
from reflex.base import Base


class Route(Base):
    """A page route."""

    # The path of the route.
    path: str

    # The page title.
    title: Union[str, None] = None

    # The component to render for the route.
    component: Union[rx.Component, Callable[[], rx.Component]]


def get_path(component_fn: Callable):
    """Get the path for a page based on the file location.

    Args:
        component_fn: The component function for the page.
    """
    module = inspect.getmodule(component_fn)

    # Create a path based on the module name.
    return (
        module.__name__.replace(".", "/").replace("_", "-").split("the_daily_bite_web_app/pages")[1]
    )
