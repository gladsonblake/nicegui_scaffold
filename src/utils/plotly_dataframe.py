"""Utilities for converting pandas DataFrames to Plotly figure dictionaries.

These functions produce dictionaries compatible with the NiceGUI Plotly
JavaScript interface, which is more efficient for plots with many data points.
"""

from typing import TYPE_CHECKING, Any, Literal

import pandas as pd

if TYPE_CHECKING:
    from .plotly_theme import PlotlyTheme


def dataframe_to_plotly(
    df: pd.DataFrame,
    x_column: str,
    y_columns: str | list[str],
    chart_type: Literal["bar", "line", "scatter"] = "scatter",
    layout: dict[str, Any] | None = None,
    trace_names: list[str] | None = None,
    trace_options: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Convert a pandas DataFrame to a Plotly figure dictionary.

    Creates a dictionary structure that maps directly to the JavaScript Plotly API,
    suitable for use with NiceGUI's ui.plotly() component.

    Args:
        df: pandas DataFrame containing the data.
        x_column: Column name for x-axis values.
        y_columns: Single column name or list of column names for y-axis.
            Each column becomes a separate trace.
        chart_type: Type of chart - "bar", "line", or "scatter".
        layout: Optional dictionary of Plotly layout properties.
            Merged with sensible defaults.
        trace_names: Optional list of display names for traces.
            Defaults to column names if not provided.
        trace_options: Optional dict of additional trace properties
            to apply to all traces (e.g., marker colors, line styles).

    Returns:
        Dictionary in Plotly JS format: {"data": [...], "layout": {...}}

    Example:
        >>> df = pd.DataFrame({"month": ["Jan", "Feb"], "sales": [100, 150]})
        >>> fig = dataframe_to_plotly(df, "month", "sales", chart_type="bar")
        >>> ui.plotly(fig)
    """
    # Normalize y_columns to a list
    if isinstance(y_columns, str):
        y_columns = [y_columns]

    # Validate columns exist
    missing_cols = [c for c in [x_column, *y_columns] if c not in df.columns]
    if missing_cols:
        raise ValueError(f"Columns not found in DataFrame: {missing_cols}")

    # Set default trace names to column names
    if trace_names is None:
        trace_names = y_columns
    elif len(trace_names) != len(y_columns):
        raise ValueError(f"trace_names length ({len(trace_names)}) must match y_columns length ({len(y_columns)})")

    # Extract x values
    x_values = df[x_column].tolist()

    # Build traces
    traces = []
    for y_col, name in zip(y_columns, trace_names):
        y_values = df[y_col].tolist()
        trace = _create_trace(
            x_values=x_values,
            y_values=y_values,
            name=name,
            chart_type=chart_type,
            extra_options=trace_options,
        )
        traces.append(trace)

    # Build layout with defaults
    default_layout: dict[str, Any] = {
        "margin": {"l": 40, "r": 20, "t": 40, "b": 40},
    }

    # Add barmode for multiple bar traces
    if chart_type == "bar" and len(traces) > 1:
        default_layout["barmode"] = "group"

    # Merge user layout over defaults
    if layout:
        default_layout = _deep_merge(default_layout, layout)

    return {
        "data": traces,
        "layout": default_layout,
    }


def _create_trace(
    x_values: list,
    y_values: list,
    name: str,
    chart_type: Literal["bar", "line", "scatter"],
    extra_options: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Create a single trace dictionary for the given chart type.

    Args:
        x_values: List of x-axis values.
        y_values: List of y-axis values.
        name: Display name for the trace.
        chart_type: Type of chart.
        extra_options: Additional trace properties to merge.

    Returns:
        Trace dictionary compatible with Plotly JS API.
    """
    trace: dict[str, Any] = {
        "x": x_values,
        "y": y_values,
        "name": name,
    }

    if chart_type == "bar":
        trace["type"] = "bar"
    elif chart_type == "line":
        trace["type"] = "scatter"
        trace["mode"] = "lines"
        trace["line"] = {"width": 2}
    elif chart_type == "scatter":
        trace["type"] = "scatter"
        trace["mode"] = "markers"
        trace["marker"] = {"size": 10}
    else:
        raise ValueError(f"Unsupported chart_type: {chart_type}")

    # Merge extra options if provided
    if extra_options:
        trace = _deep_merge(trace, extra_options)

    return trace


def _deep_merge(base: dict, override: dict) -> dict:
    """Deep merge two dictionaries, with override taking precedence.

    Args:
        base: Base dictionary.
        override: Dictionary with values to override.

    Returns:
        New merged dictionary.
    """
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def apply_theme_to_figure(
    figure: dict[str, Any],
    theme: "PlotlyTheme",
    title: str | None = None,
    xaxis_title: str | None = None,
    yaxis_title: str | None = None,
) -> dict[str, Any]:
    """Apply PlotlyTheme styling to a Plotly figure dictionary.

    Merges theme colors and styling into an existing figure dictionary,
    allowing you to combine dataframe_to_plotly() output with theme support.

    Args:
        figure: Existing Plotly figure dictionary (with "data" and "layout").
        theme: PlotlyTheme instance for colors and styling.
        title: Optional chart title override.
        xaxis_title: Optional x-axis title.
        yaxis_title: Optional y-axis title.

    Returns:
        New figure dictionary with theme applied.

    Example:
        >>> fig = dataframe_to_plotly(df, "x", "y")
        >>> theme = PlotlyTheme.from_layout(layout)
        >>> themed_fig = apply_theme_to_figure(fig, theme, title="My Chart")
        >>> ui.plotly(themed_fig)
    """
    # Get theme colors
    bg_color, text_color, grid_color = theme.get_colors()

    # Build theme layout
    theme_layout: dict[str, Any] = {
        "plot_bgcolor": bg_color,
        "paper_bgcolor": bg_color,
        "font": {"color": text_color},
        "xaxis": {
            "gridcolor": grid_color,
            "linecolor": text_color,
            "zerolinecolor": grid_color,
        },
        "yaxis": {
            "gridcolor": grid_color,
            "linecolor": text_color,
            "zerolinecolor": grid_color,
        },
    }

    # Add optional titles
    if title is not None:
        theme_layout["title"] = title
    if xaxis_title is not None:
        theme_layout["xaxis"]["title"] = xaxis_title
    if yaxis_title is not None:
        theme_layout["yaxis"]["title"] = yaxis_title

    # Merge theme layout with existing figure layout
    # Theme layout goes first, then existing layout overrides
    existing_layout = figure.get("layout", {})
    merged_layout = _deep_merge(theme_layout, existing_layout)

    # If titles were provided, they should override existing
    if title is not None:
        merged_layout["title"] = title
    if xaxis_title is not None:
        if "xaxis" not in merged_layout:
            merged_layout["xaxis"] = {}
        merged_layout["xaxis"]["title"] = xaxis_title
    if yaxis_title is not None:
        if "yaxis" not in merged_layout:
            merged_layout["yaxis"] = {}
        merged_layout["yaxis"]["title"] = yaxis_title

    return {
        "data": figure.get("data", []),
        "layout": merged_layout,
    }
