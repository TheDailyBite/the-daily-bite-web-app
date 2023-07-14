from .base import BaseState


class NavbarState(BaseState):
    """The state for the navbar component."""

    # Whether the sidebar is open.
    sidebar_open: bool = False

    def toggle_sidebar(self):
        """Toggle the sidebar open state."""
        self.sidebar_open = not self.sidebar_open
