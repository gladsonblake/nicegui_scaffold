from nicegui import ui

from components import PageLayout


@PageLayout(
    header_content=lambda: ui.label("NiceGUI Scaffold").classes("text-xl font-bold"),
    # footer_content=lambda: ui.label("© 2024 My App. All rights reserved.").classes("text-sm"),
    left_drawer_content=lambda layout: layout.render_navigation(),
)
def home(layout: PageLayout):
    """Home page with full layout example."""
    with ui.column().classes("p-6 gap-4 w-full max-w-4xl mx-auto"):
        ui.label("Welcome to the Home Page").classes("text-3xl font-bold mb-4")
        ui.label("This page demonstrates a full layout with header, footer, and both drawers.")

        with ui.card().classes("p-4"):
            ui.label("Page Content").classes("text-xl font-semibold mb-2")
            ui.label("You can add any content here. The layout provides a consistent structure across all pages.")

        # Add some sample content to demonstrate scrolling
        for i in range(20):
            with ui.card().classes("p-4"):
                ui.label(f"Content Section {i + 1}").classes("font-semibold")
                ui.label(f"This is section {i + 1} of the page content.")
