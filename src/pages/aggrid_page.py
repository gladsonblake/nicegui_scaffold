import pandas as pd
from nicegui import ui

from components import PageLayout


def get_filter_type(dtype):
    """Return the appropriate AG Grid filter type based on pandas dtype."""
    if pd.api.types.is_datetime64_any_dtype(dtype):
        return "agDateColumnFilter"
    elif pd.api.types.is_integer_dtype(dtype) or pd.api.types.is_float_dtype(dtype):
        return "agNumberColumnFilter"
    else:
        return "agTextColumnFilter"


def create_options_for_aggrid_from_df(
    df: pd.DataFrame, filters: bool = True, theme: str = "balham", row_selection_mode: str | None = None
) -> dict:
    """From a dataframe, returns the columnDefs and rowSelection objects for aggrid options.

    This function creates AG Grid options that can be passed to ui.aggrid.from_pandas() via the options parameter.
    Note: rowData is not included as it's handled by from_pandas().

    Args:
        df: The pandas DataFrame to generate column definitions from
        filters: Whether to enable filters on columns (default: True)
        theme: AG Grid theme (not used in options, passed separately to from_pandas)
        row_selection_mode: Row selection mode ('single', 'multiple', or None)

    Returns:
        Dictionary with 'columnDefs' and optionally 'rowSelection' keys
    """
    options: dict = {
        "columnDefs": [],
    }

    # Always create columnDefs for all columns
    for column in df.columns:
        column_def = {
            "field": str(column),
            "headerName": str(column).title(),
        }
        # Add filter if enabled
        if filters:
            filter_type = get_filter_type(df[column].dtype)
            column_def["filter"] = filter_type
            column_def["floatingFilter"] = True
        options["columnDefs"].append(column_def)

    # Only include rowSelection if specified
    if row_selection_mode:
        options["rowSelection"] = row_selection_mode

    return options


@PageLayout(
    header_content=lambda: ui.label("AgGrid Demo").classes("text-xl font-bold"),
    left_drawer_content=lambda layout: layout.render_navigation(),
)
def _aggrid_page(layout: PageLayout):
    df = pd.read_csv("data/sample_data.csv")
    # Convert month to datetime
    df["month"] = pd.to_datetime(df["month"])

    df["example_site"] = (
        '<a href="https://google.com" target="_blank" rel="noopener noreferrer" class="inline-block px-3 py-1.5 bg-blue-500 hover:bg-blue-600 text-white text-xs font-medium rounded transition-colors no-underline">Go to Google</a>'
    )

    options = create_options_for_aggrid_from_df(df, filters=True, theme="balham", row_selection_mode="multiple")

    aggrid = ui.aggrid.from_pandas(df, theme="balham", options=options, html_columns=[len(df.columns) - 1]).classes(
        "h-[70dvh]"
    )
