from nicegui import ui

from components import PageLayout

from .shared import _render_settings


@PageLayout(
    header_content=lambda: ui.label("Drawer Demo").classes("text-xl font-bold"),
    left_drawer_content=PageLayout.render_navigation,
    right_drawer_content=_render_settings,
)
def drawers_page(layout: PageLayout):
    """Page with drawers and header."""
    with ui.column().classes("p-6 gap-4 w-full max-w-4xl mx-auto"):
        ui.label("Drawers Example").classes("text-3xl font-bold mb-4")
        ui.label("This page has both left and right drawers with toggle buttons in the header.")
        ui.label("On desktop, drawers auto-show. On mobile, use the menu buttons to toggle them.")
