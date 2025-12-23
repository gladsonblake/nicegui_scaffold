"""Plotly page demonstrating chart interaction with theme support."""

import pandas as pd
from nicegui import ui

from components import PageLayout
from utils import PlotlyEventHandler, PlotlyTheme
from utils.plotly_dataframe import apply_theme_to_figure, dataframe_to_plotly
from utils.plotly_events import PlotlyClickEvent, PlotlySelectEvent

# Chart titles
MAIN_CHART_TITLE = "Monthly Trends - Click or select a month"
DERIVATIVE_CHART_TITLE = "Month Metrics"

# Metrics to display in derivative chart
METRICS = ["sales", "revenue", "profit", "visitors"]


@PageLayout(
    header_content=lambda: ui.label("Plotly Charts Demo").classes("text-xl font-bold"),
    left_drawer_content=lambda layout: layout.render_navigation(),
)
def _plotly_page(layout: PageLayout):
    """Plotly page demonstrating chart interaction."""
    # Load CSV data once
    df = pd.read_csv("data/sample_data.csv")

    # Initialize theme helper
    theme = PlotlyTheme.from_layout(layout)

    def create_main_figure() -> dict:
        """Create the main trends chart from CSV data."""
        fig = dataframe_to_plotly(
            df,
            x_column="month",
            y_columns=["sales", "revenue"],
            chart_type="scatter",
        )
        return apply_theme_to_figure(
            fig,
            theme,
            title=MAIN_CHART_TITLE,
            xaxis_title="Month",
            yaxis_title="Value",
        )

    def create_derivative_figure(month: str | None = None) -> dict:
        """Create derivative chart showing all metrics for a selected month."""
        if month is None:
            # Empty chart when no selection
            return apply_theme_to_figure(
                {"data": [], "layout": {}},
                theme,
                title=DERIVATIVE_CHART_TITLE,
                xaxis_title="Metric",
                yaxis_title="Value",
            )

        # Get data for the selected month
        row = df[df["month"] == month]
        if row.empty:
            return create_derivative_figure(None)

        row_data = row.iloc[0]
        values = [row_data[metric] for metric in METRICS]

        fig = dataframe_to_plotly(
            pd.DataFrame({"metric": METRICS, "value": values}),
            x_column="metric",
            y_columns="value",
            chart_type="bar",
        )
        return apply_theme_to_figure(
            fig,
            theme,
            title=f"{month} Metrics",
            xaxis_title="Metric",
            yaxis_title="Value",
        )

    def update_derivative_chart(month: str | None) -> None:
        """Update the derivative chart with data for the given month."""
        derivative_plot.update_figure(create_derivative_figure(month))

    def handle_click(event: PlotlyClickEvent) -> None:
        """Handle click on main chart - show metrics for clicked month."""
        point = event.first_point
        filtered_df = event.filter_dataframe_on_x(df, "month")
        ui.notify(filtered_df.to_string())
        ui.notify(event.y_values)
        if point and point.x in df["month"].values:
            update_derivative_chart(point.x)
            ui.notify(f"Showing metrics for {point.x}")

    def handle_select(event: PlotlySelectEvent) -> None:
        """Handle selection on main chart - show metrics for first selected month."""

        filtered_df = event.filter_dataframe_on_x(df, "month")
        ui.notify(filtered_df.to_string())
        ui.aggrid.from_pandas(
            filtered_df,
            theme="balham",
            options={
                "columnDefs": [
                    {"field": "month", "headerName": "Month", "filter": "agTextColumnFilter", "floatingFilter": True}
                ]
            },
        ).classes("max-h-40")
        if event.is_empty:
            update_derivative_chart(None)
            return

        filtered_df = event.filter_dataframe(df, "month", ["sales", "revenue"])
        ui.notify(filtered_df.to_string())

        # Use the first selected point
        first_month = event.x_values[0] if event.x_values else None
        if first_month and first_month in df["month"].values:
            update_derivative_chart(first_month)
            ui.notify(f"Selected {event.point_count} point(s) - showing {first_month}")

    @ui.refreshable
    def main_chart() -> None:
        """Render the main trends chart."""
        plot = ui.plotly(create_main_figure())
        handler = PlotlyEventHandler(plot)
        handler.on_click(handle_click).on_select(handle_select)

    def update_chart_themes(_=None) -> None:
        """Update charts when theme changes."""
        main_chart.refresh()
        # Preserve current derivative chart state by re-applying theme
        current_fig = derivative_plot.figure
        if current_fig and current_fig.get("layout", {}).get("title"):
            title = current_fig["layout"]["title"]
            # Extract month from title if it exists (format: "MonthName Metrics")
            if title != DERIVATIVE_CHART_TITLE and title.endswith(" Metrics"):
                month = title.replace(" Metrics", "")
                update_derivative_chart(month)
            else:
                update_derivative_chart(None)
        else:
            update_derivative_chart(None)

    # Page content - two charts side by side
    with ui.grid(columns=2).classes("w-full gap-4"):
        with ui.column().classes("w-full"):
            main_chart()

        with ui.column().classes("w-full"):
            derivative_plot = ui.plotly(create_derivative_figure(None))

    layout.on_dark_mode_change(update_chart_themes)
