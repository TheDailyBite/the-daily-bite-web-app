from .base import BaseState


class IndexState(BaseState):
    """Hold the state for the home page."""

    # Whether to show the call to action.
    show_c2a: bool = True

    def close_c2a(self):
        """Close the call to action."""
        self.show_c2a = False
