import plotly.graph_objects as go
from nicegui import ui

from components import PageLayout

from .shared import _render_settings


@PageLayout(
    header_content=lambda: ui.label("Drawer Demo").classes("text-xl font-bold"),
    left_drawer_content=lambda layout: layout.render_navigation(),
    right_drawer_content=_render_settings,
)
def drawers_page(layout: PageLayout):
    """Page with drawers and header."""
    with ui.column().classes("p-6 gap-4 w-full max-w-4xl mx-auto"):
        ui.label("Drawers Example").classes("text-3xl font-bold mb-4")
        ui.label("This page has both left and right drawers with toggle buttons in the header.")
        ui.label("On desktop, drawers auto-show. On mobile, use the menu buttons to toggle them.")

        fig = go.Figure(go.Scatter(x=[1, 2, 3, 4], y=[1, 2, 3, 2.5]))
        fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))
        plot = ui.plotly(fig).classes("w-full h-40")

        plot.on("plotly_selected", ui.notify)
