"""Main entry point for the NiceGUI application.

Demonstrates the PageLayout component with various configuration options.
"""

from pages.drawer_page import drawers_page
from pages.home_page import home

from nicegui import ui


@ui.page("/")
def index_page():
    home()


@ui.page("/drawers-only")
def drawers_only_page():
    drawers_page()


if __name__ in {"__main__", "__mp_main__"}:
    ui.run(
        title="NiceGUI Layout Demo",
        port=8080,
        dark=None,
        storage_secret="nicegui-scaffold-secret-key",
    )
