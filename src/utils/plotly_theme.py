"""Plotly theme utilities for NiceGUI applications.

Provides theme-aware chart configuration that integrates with the PageLayout
color scheme and dark mode settings.
"""

from typing import Any, Optional

import plotly.graph_objects as go
from nicegui import app


class PlotlyTheme:
    """Theme-aware Plotly chart configuration.

    Integrates with PageLayout to provide consistent chart styling that
    automatically adapts to light/dark mode and uses the app's color scheme.

    Example:
        ```python
        theme = PlotlyTheme(layout)
        fig = go.Figure(go.Bar(x=[1, 2], y=[3, 4]))
        fig.update_layout(**theme.get_layout("My Chart", "X Axis", "Y Axis"))
        ```
    """

    def __init__(
        self,
        dark_page_color: str = "#121212",
        light_page_color: str = "white",
        primary_color: str = "#22c55e",
        secondary_color: str = "#3b82f6",
    ):
        """Initialize PlotlyTheme.

        Args:
            dark_page_color: Background color for dark mode.
            light_page_color: Background color for light mode.
            primary_color: Primary chart color (e.g., for line charts).
            secondary_color: Secondary chart color (e.g., for bar charts).
        """
        self.dark_page_color = dark_page_color
        self.light_page_color = light_page_color
        self.primary_color = primary_color
        self.secondary_color = secondary_color

    @classmethod
    def from_layout(cls, layout: Any) -> "PlotlyTheme":
        """Create a PlotlyTheme from a PageLayout instance.

        Args:
            layout: A PageLayout instance with color configuration.

        Returns:
            PlotlyTheme configured with the layout's colors.
        """
        return cls(
            dark_page_color=getattr(layout, "dark_page_color", "#121212"),
            light_page_color="white",
            primary_color=getattr(layout, "primary_color", "#22c55e"),
        )

    def is_dark_mode(self) -> bool:
        """Check if dark mode is currently active."""
        return app.storage.user.get("dark_mode", True)

    def get_colors(self) -> tuple[str, str, str]:
        """Get current theme colors.

        Returns:
            Tuple of (background_color, text_color, grid_color).
        """
        is_dark = self.is_dark_mode()
        bg_color = self.dark_page_color if is_dark else self.light_page_color
        text_color = "white" if is_dark else "black"
        grid_color = "rgba(255, 255, 255, 0.1)" if is_dark else "rgba(0, 0, 0, 0.1)"
        return bg_color, text_color, grid_color

    def get_layout(
        self,
        title: str,
        xaxis_title: str,
        yaxis_title: str,
        yaxis_range: Optional[list] = None,
        **kwargs: Any,
    ) -> dict:
        """Get a theme-aware layout configuration for Plotly.

        Args:
            title: Chart title.
            xaxis_title: X-axis label.
            yaxis_title: Y-axis label.
            yaxis_range: Optional [min, max] range for Y-axis.
            **kwargs: Additional layout properties to merge.

        Returns:
            Dictionary suitable for fig.update_layout(**layout).
        """
        bg_color, text_color, grid_color = self.get_colors()

        layout_dict = {
            "margin": dict(l=40, r=20, t=40, b=40),
            "title": title,
            "xaxis_title": xaxis_title,
            "yaxis_title": yaxis_title,
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

        if yaxis_range:
            layout_dict["yaxis"]["range"] = yaxis_range

        # Merge any additional kwargs
        layout_dict.update(kwargs)

        return layout_dict

    def create_scatter(
        self,
        x: list,
        y: list,
        mode: str = "markers+lines",
        name: str = "Data",
        marker_size: int = 10,
        color: Optional[str] = None,
    ) -> go.Scatter:
        """Create a themed scatter trace.

        Args:
            x: X-axis data.
            y: Y-axis data.
            mode: Plotly mode ('markers', 'lines', 'markers+lines').
            name: Trace name for legend.
            marker_size: Size of markers.
            color: Override color (defaults to primary_color).

        Returns:
            Plotly Scatter trace.
        """
        return go.Scatter(
            x=x,
            y=y,
            mode=mode,
            marker=dict(size=marker_size, color=color or self.primary_color),
            name=name,
        )

    def create_bar(
        self,
        x: list,
        y: list,
        name: str = "Data",
        color: Optional[str] = None,
    ) -> go.Bar:
        """Create a themed bar trace.

        Args:
            x: X-axis data (categories).
            y: Y-axis data (values).
            name: Trace name for legend.
            color: Override color (defaults to secondary_color).

        Returns:
            Plotly Bar trace.
        """
        return go.Bar(
            x=x,
            y=y,
            marker_color=color or self.secondary_color,
            name=name,
        )

    def create_figure(
        self,
        trace: Any,
        title: str,
        xaxis_title: str,
        yaxis_title: str,
        yaxis_range: Optional[list] = None,
        **layout_kwargs: Any,
    ) -> go.Figure:
        """Create a complete themed figure.

        Args:
            trace: Plotly trace (Scatter, Bar, etc.).
            title: Chart title.
            xaxis_title: X-axis label.
            yaxis_title: Y-axis label.
            yaxis_range: Optional [min, max] range for Y-axis.
            **layout_kwargs: Additional layout properties.

        Returns:
            Complete Plotly Figure with theming applied.
        """
        fig = go.Figure(trace)
        fig.update_layout(
            **self.get_layout(
                title=title,
                xaxis_title=xaxis_title,
                yaxis_title=yaxis_title,
                yaxis_range=yaxis_range,
                **layout_kwargs,
            )
        )
        return fig
