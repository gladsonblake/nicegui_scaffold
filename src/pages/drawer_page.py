from components import PageLayout

from nicegui import ui

from .shared import _render_settings


@PageLayout(
    left_drawer_content=PageLayout.render_navigation,
    right_drawer_content=_render_settings,
)
def drawers_page(layout: PageLayout):
    """Page with only drawers, no header or footer."""
    # Add floating toggle buttons for the drawers using page_sticky

    # Right drawer toggle button
    with ui.page_sticky(position="top-right", x_offset=16, y_offset=16):
        ui.button(
            icon="menu",
            on_click=lambda: layout.right_drawer.toggle() if layout.right_drawer else None,
            color=None,
        ).props("round").classes("shadow-lg")

    with ui.column().classes("p-6 gap-4 w-full max-w-4xl mx-auto"):
        ui.label("Drawers Only Example").classes("text-3xl font-bold mb-4")
        ui.label("This page has collapsible drawers but no header or footer.")
        ui.label("Click the menu buttons in the top corners to toggle the drawers.")
