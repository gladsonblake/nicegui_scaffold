"""Plotly page demonstrating chart interaction with theme support."""

import json
import random

import plotly.graph_objects as go
from nicegui import app, ui

from components import PageLayout
from utils import PlotlyTheme

# Constants for chart configuration
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
SOURCE_CHART_TITLE = "Source Chart - Select points to update the chart below"
TARGET_CHART_TITLE = "Target Chart - Updated from selection above"


@PageLayout(
    header_content=lambda: ui.label("Plotly Charts Demo").classes("text-xl font-bold"),
    left_drawer_content=lambda layout: layout.render_navigation(),
)
def _plotly_page(layout: PageLayout):
    """Plotly page demonstrating chart interaction."""
    # Initialize theme helper
    theme = PlotlyTheme.from_layout(layout)

    # Generate reproducible fake data
    random.seed(42)
    sales_data = [random.randint(20, 100) for _ in range(12)]

    def _get_selected_indices() -> list[int]:
        return list(app.storage.client.get("plotly_selected_indices", []))

    def _set_selected_indices(indices: list[int]) -> None:
        # Keep it small, stable, and JSON-serializable
        app.storage.client["plotly_selected_indices"] = sorted(set(int(i) for i in indices))

    def create_source_figure() -> go.Figure:
        """Create the source scatter chart."""
        trace = theme.create_scatter(
            x=MONTHS,
            y=sales_data,
            name="Monthly Sales",
        )
        selected_indices = _get_selected_indices()
        if selected_indices:
            trace.selectedpoints = selected_indices
        return theme.create_figure(
            trace=trace,
            title=SOURCE_CHART_TITLE,
            xaxis_title="Month",
            yaxis_title="Sales",
            dragmode="select",
        )

    def create_target_figure(x: list, y: list) -> go.Figure:
        """Create the target bar chart with given data."""
        return theme.create_figure(
            trace=theme.create_bar(x=x, y=y, name="Selected Sales"),
            title=TARGET_CHART_TITLE,
            xaxis_title="Month",
            yaxis_title="Sales",
        )

    def update_bar_chart(x_values: list, y_values: list) -> None:
        """Update the bar chart with new data."""
        plot2.update_figure(create_target_figure(x_values, y_values))

    # Event handlers
    def handle_selection(event):
        """Update the bar chart based on selected points."""
        if event.args:
            event_str = json.dumps(event.args, indent=2)
            ui.run_javascript(f"console.log({event_str})")

        if event.args and "points" in event.args:
            points = event.args["points"]
            if points:
                x_values = [p.get("x") for p in points]
                y_values = [p.get("y") for p in points]
                selected_indices = [i for i, month in enumerate(MONTHS) if month in set(x_values)]
                _set_selected_indices(selected_indices)
                update_bar_chart(x_values, y_values)
                ui.notify(f"Updated chart with {len(points)} selected point(s)")
                return

        # Clear chart if no valid selection
        _set_selected_indices([])
        update_bar_chart([], [])

    def handle_click(event):
        """Update the bar chart based on a single clicked point."""
        if event.args and "points" in event.args:
            points = event.args["points"]
            if points:
                point = points[0]
                x_value = point.get("x")
                y_value = point.get("y")
                if x_value in MONTHS:
                    _set_selected_indices([MONTHS.index(x_value)])
                update_bar_chart([x_value], [y_value])
                ui.notify(f"Selected: {x_value} - Sales: {y_value}")

    # Theme change handler
    def update_chart_themes(_=None):
        """Update both charts with current theme."""
        source_chart.refresh()
        # Preserve existing bar chart data
        current_fig = plot2.figure
        if current_fig and len(current_fig.data) > 0:
            trace = current_fig.data[0]
            x_data = list(trace.x) if trace.x is not None else []
            y_data = list(trace.y) if trace.y is not None else []
            update_bar_chart(x_data, y_data)
        else:
            update_bar_chart([], [])

    @ui.refreshable
    def source_chart() -> None:
        plot1 = ui.plotly(create_source_figure())
        plot1.on("plotly_selected", handle_selection)
        plot1.on("plotly_click", handle_click)

    # Page content
    with ui.grid(columns=2):
        with ui.column():
            source_chart()

        with ui.column():
            plot2 = ui.plotly(create_target_figure([], []))

            layout.on_dark_mode_change(update_chart_themes)
