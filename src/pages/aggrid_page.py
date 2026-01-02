from typing import Literal

import pandas as pd
from nicegui import ui

from components import PageLayout
from utils import PlotlyTheme
from utils.plotly_dataframe import apply_theme_to_figure, dataframe_to_plotly

RowSelectionMode = Literal["singleRow", "multiRow"]


def _get_filter_type(dtype) -> str:
    """Return the appropriate AG Grid filter type based on pandas dtype."""
    if pd.api.types.is_datetime64_any_dtype(dtype):
        return "agDateColumnFilter"
    elif pd.api.types.is_integer_dtype(dtype) or pd.api.types.is_float_dtype(dtype):
        return "agNumberColumnFilter"
    else:
        return "agTextColumnFilter"


def aggrid_from_pandas(
    df: pd.DataFrame,
    *,
    html_columns: list[str] | None = None,
    editable: bool = False,
    filters: bool = True,
    theme: str = "balham",
    row_selection_mode: RowSelectionMode | None = None,
) -> ui.aggrid:
    """Create an AG Grid from a pandas DataFrame with sensible defaults.

    Args:
        df: The pandas DataFrame to create the AG Grid from
        html_columns: Column names to render as HTML
        editable: Whether to enable editing on columns
        filters: Whether to enable filters on columns
        theme: The AG Grid theme to use
        row_selection_mode: Row selection mode ('singleRow' or 'multiRow')

    Returns:
        The AG Grid component
    """
    # Build column definitions
    column_defs = []
    for column in df.columns:
        column_def = {
            "field": str(column),
            "headerName": " ".join(word.capitalize() for word in str(column).replace("_", " ").split()),
            "editable": editable,
        }
        if filters:
            column_def["filter"] = _get_filter_type(df[column].dtype)
            column_def["floatingFilter"] = True
        column_defs.append(column_def)

    # Build options
    options: dict = {"columnDefs": column_defs}
    if row_selection_mode:
        options["rowSelection"] = {"mode": row_selection_mode}

    # Convert html_columns names to indices
    html_column_indices = [df.columns.get_loc(col) for col in html_columns] if html_columns else []

    return ui.aggrid.from_pandas(df, theme=theme, options=options, html_columns=html_column_indices)


@PageLayout(
    header_content=lambda: ui.label("AgGrid Demo").classes("text-xl font-bold"),
    left_drawer_content=lambda layout: layout.render_navigation(),
)
def _aggrid_page(layout: PageLayout):
    df = pd.read_csv("data/sample_data.csv")
    # Convert month to datetime
    df["month"] = pd.to_datetime(df["month"])

    df["example_site"] = (
        '<a href="https://google.com" target="_blank" rel="noopener noreferrer" class="  inline-block px-3 py-1.5 bg-blue-500 hover:bg-blue-600 text-white text-xs font-medium rounded transition-colors no-underline w-full text-center">Go to Google</a>'
    )

    aggrid = aggrid_from_pandas(
        df, html_columns=["example_site"], editable=True, filters=True, theme="balham", row_selection_mode="singleRow"
    ).classes("h-[50dvh]")

    async def get_filtered_dataframe(aggrid: ui.aggrid) -> pd.DataFrame:
        """Get the currently filtered data from AG Grid as a DataFrame."""
        filtered_data = await aggrid.get_client_data(method="filtered_unsorted")
        return pd.DataFrame(filtered_data)

    @ui.refreshable
    async def update_plot():
        """Update the plot with filtered data from AG Grid."""
        filtered_df = await get_filtered_dataframe(aggrid)
        ui.plotly(
            apply_theme_to_figure(
                dataframe_to_plotly(filtered_df, x_column="month", y_columns=["sales", "revenue"]),
                theme=PlotlyTheme.from_layout(layout),
            )
        )

    print(aggrid.on("cellValueChanged", lambda e: print(e)))
    aggrid.on("filterChanged", lambda e: update_plot.refresh())
    # Create initial plot with all data
    update_plot()

    layout.on_dark_mode_change(lambda _: update_plot.refresh())
