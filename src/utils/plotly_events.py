"""Typed dataclasses and event handler for Plotly chart interactions.

This module provides a clean API for handling Plotly events in NiceGUI,
parsing raw event data into typed dataclasses for easier consumption
in derivative charts and tables.
"""

from dataclasses import dataclass, field
from typing import Any, Callable

from nicegui.elements.plotly import Plotly


@dataclass
class PlotlyPoint:
    """Represents a single data point from a Plotly event.

    Attributes:
        x: X-axis value of the point.
        y: Y-axis value of the point.
        curve_number: Index of the trace in the figure data array.
        point_number: Index of the point within the trace.
        z: Z-axis value for 3D charts (optional).
        lat: Latitude for map charts (optional).
        lon: Longitude for map charts (optional).
        text: Text annotation associated with the point (optional).
        customdata: Custom data attached to the point (optional).
        point_numbers: List of point indices for histogram bins (optional).
    """

    x: Any
    y: Any
    curve_number: int
    point_number: int
    z: Any | None = None
    lat: float | None = None
    lon: float | None = None
    text: str | None = None
    customdata: Any | None = None
    point_numbers: list[int] | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PlotlyPoint":
        """Create a PlotlyPoint from a Plotly event point dictionary.

        Args:
            data: Dictionary containing point data from Plotly event.

        Returns:
            PlotlyPoint instance with parsed data.
        """
        return cls(
            x=data.get("x"),
            y=data.get("y"),
            curve_number=data.get("curveNumber", 0),
            point_number=data.get("pointNumber", 0),
            z=data.get("z"),
            lat=data.get("lat"),
            lon=data.get("lon"),
            text=data.get("text"),
            customdata=data.get("customdata"),
            point_numbers=data.get("pointNumbers"),
        )


@dataclass
class PlotlyClickEvent:
    """Event data from a plotly_click event.

    Attributes:
        points: List of clicked points.
    """

    points: list[PlotlyPoint] = field(default_factory=list)

    @property
    def x_values(self) -> list[Any]:
        """Get all x values from clicked points."""
        return [p.x for p in self.points]

    @property
    def y_values(self) -> list[Any]:
        """Get all y values from clicked points."""
        return [p.y for p in self.points]

    @property
    def first_point(self) -> PlotlyPoint | None:
        """Get the first clicked point, or None if no points."""
        return self.points[0] if self.points else None

    @classmethod
    def from_event_args(cls, args: dict[str, Any] | None) -> "PlotlyClickEvent":
        """Create a PlotlyClickEvent from raw event args.

        Args:
            args: Raw event.args dictionary from NiceGUI event.

        Returns:
            PlotlyClickEvent instance with parsed points.
        """
        if not args or "points" not in args:
            return cls(points=[])

        points = [PlotlyPoint.from_dict(p) for p in args["points"]]
        return cls(points=points)


@dataclass
class PlotlyHoverEvent:
    """Event data from plotly_hover and plotly_unhover events.

    Attributes:
        points: List of hovered points.
    """

    points: list[PlotlyPoint] = field(default_factory=list)

    @property
    def x_values(self) -> list[Any]:
        """Get all x values from hovered points."""
        return [p.x for p in self.points]

    @property
    def y_values(self) -> list[Any]:
        """Get all y values from hovered points."""
        return [p.y for p in self.points]

    @property
    def first_point(self) -> PlotlyPoint | None:
        """Get the first hovered point, or None if no points."""
        return self.points[0] if self.points else None

    @classmethod
    def from_event_args(cls, args: dict[str, Any] | None) -> "PlotlyHoverEvent":
        """Create a PlotlyHoverEvent from raw event args.

        Args:
            args: Raw event.args dictionary from NiceGUI event.

        Returns:
            PlotlyHoverEvent instance with parsed points.
        """
        if not args or "points" not in args:
            return cls(points=[])

        points = [PlotlyPoint.from_dict(p) for p in args["points"]]
        return cls(points=points)


@dataclass
class PlotlySelectEvent:
    """Event data from plotly_selected and plotly_selecting events.

    Attributes:
        points: List of selected points.
        range: Selection range for box/rect selection (optional).
        lassoPoints: Lasso selection coordinates (optional).
    """

    points: list[PlotlyPoint] = field(default_factory=list)
    range: dict[str, Any] | None = None
    lassoPoints: dict[str, Any] | None = None

    @property
    def x_values(self) -> list[Any]:
        """Get all x values from selected points."""
        return [p.x for p in self.points]

    @property
    def y_values(self) -> list[Any]:
        """Get all y values from selected points."""
        return [p.y for p in self.points]

    @property
    def point_count(self) -> int:
        """Get the number of selected points."""
        return len(self.points)

    @property
    def is_empty(self) -> bool:
        """Check if the selection is empty."""
        return len(self.points) == 0

    @classmethod
    def from_event_args(cls, args: dict[str, Any] | None) -> "PlotlySelectEvent":
        """Create a PlotlySelectEvent from raw event args.

        Args:
            args: Raw event.args dictionary from NiceGUI event.

        Returns:
            PlotlySelectEvent instance with parsed points and selection info.
        """
        if not args:
            return cls(points=[])

        points = []
        if "points" in args:
            points = [PlotlyPoint.from_dict(p) for p in args["points"]]

        return cls(
            points=points,
            range=args.get("range"),
            lassoPoints=args.get("lassoPoints"),
        )


@dataclass
class PlotlyLegendClickEvent:
    """Event data from plotly_legendclick and plotly_legenddoubleclick events.

    Note: The `data` and `fullData` properties from Plotly events contain
    circular references and cannot be serialized to JSON. Only simple
    properties are available.

    Attributes:
        curve_number: Index of the trace whose legend item was clicked.
        expanded_index: Index for grouped legends (optional).
    """

    curve_number: int
    expanded_index: int | None = None

    @classmethod
    def from_event_args(cls, args: dict[str, Any] | None) -> "PlotlyLegendClickEvent":
        """Create a PlotlyLegendClickEvent from raw event args.

        Args:
            args: Raw event.args dictionary from NiceGUI event.

        Returns:
            PlotlyLegendClickEvent instance with parsed data.
        """
        if not args:
            return cls(curve_number=0)

        return cls(
            curve_number=args.get("curveNumber", 0),
            expanded_index=args.get("expandedIndex"),
        )


class PlotlyEventHandler:
    """Handler for registering typed callbacks on Plotly chart events.

    Wraps a ui.plotly element and provides methods to register callbacks
    that receive parsed, typed event data instead of raw dictionaries.

    Example:
        plot = ui.plotly(fig)
        handler = PlotlyEventHandler(plot)
        handler.on_click(lambda event: print(event.x_values))
        handler.on_select(lambda event: update_table(event.points))
    """

    def __init__(self, plot: Plotly) -> None:
        """Initialize the event handler.

        Args:
            plot: The ui.plotly element to attach handlers to.
        """
        self._plot = plot

    @property
    def plot(self) -> Plotly:
        """Get the wrapped Plotly element."""
        return self._plot

    def on_click(
        self,
        callback: Callable[[PlotlyClickEvent], None],
        throttle: float = 0.0,
    ) -> "PlotlyEventHandler":
        """Register a callback for click events.

        Args:
            callback: Function to call with parsed PlotlyClickEvent.
            throttle: Minimum time between event occurrences (seconds).

        Returns:
            Self for method chaining.
        """

        def handler(event):
            parsed = PlotlyClickEvent.from_event_args(event.args)
            callback(parsed)

        self._plot.on("plotly_click", handler, throttle=throttle)
        return self

    def on_hover(
        self,
        callback: Callable[[PlotlyHoverEvent], None],
        throttle: float = 0.1,
    ) -> "PlotlyEventHandler":
        """Register a callback for hover events.

        Args:
            callback: Function to call with parsed PlotlyHoverEvent.
            throttle: Minimum time between event occurrences (seconds).
                      Defaults to 0.1 to prevent excessive calls.

        Returns:
            Self for method chaining.
        """

        def handler(event):
            parsed = PlotlyHoverEvent.from_event_args(event.args)
            callback(parsed)

        self._plot.on("plotly_hover", handler, throttle=throttle)
        return self

    def on_unhover(
        self,
        callback: Callable[[PlotlyHoverEvent], None],
        throttle: float = 0.0,
    ) -> "PlotlyEventHandler":
        """Register a callback for unhover events.

        Args:
            callback: Function to call with parsed PlotlyHoverEvent.
            throttle: Minimum time between event occurrences (seconds).

        Returns:
            Self for method chaining.
        """

        def handler(event):
            parsed = PlotlyHoverEvent.from_event_args(event.args)
            callback(parsed)

        self._plot.on("plotly_unhover", handler, throttle=throttle)
        return self

    def on_select(
        self,
        callback: Callable[[PlotlySelectEvent], None],
        throttle: float = 0.0,
    ) -> "PlotlyEventHandler":
        """Register a callback for selection complete events.

        Args:
            callback: Function to call with parsed PlotlySelectEvent.
            throttle: Minimum time between event occurrences (seconds).

        Returns:
            Self for method chaining.
        """

        def handler(event):
            parsed = PlotlySelectEvent.from_event_args(event.args)
            callback(parsed)

        self._plot.on("plotly_selected", handler, throttle=throttle)
        return self

    def on_selecting(
        self,
        callback: Callable[[PlotlySelectEvent], None],
        throttle: float = 0.1,
    ) -> "PlotlyEventHandler":
        """Register a callback for selection in-progress events.

        Args:
            callback: Function to call with parsed PlotlySelectEvent.
            throttle: Minimum time between event occurrences (seconds).
                      Defaults to 0.1 to prevent excessive calls during drag.

        Returns:
            Self for method chaining.
        """

        def handler(event):
            parsed = PlotlySelectEvent.from_event_args(event.args)
            callback(parsed)

        self._plot.on("plotly_selecting", handler, throttle=throttle)
        return self

    def on_deselect(
        self,
        callback: Callable[[], None],
    ) -> "PlotlyEventHandler":
        """Register a callback for deselection events.

        Args:
            callback: Function to call when selection is cleared.

        Returns:
            Self for method chaining.
        """

        def handler(_event):
            callback()

        self._plot.on("plotly_deselect", handler)
        return self

    def on_legend_click(
        self,
        callback: Callable[[PlotlyLegendClickEvent], None],
        throttle: float = 0.0,
    ) -> "PlotlyEventHandler":
        """Register a callback for legend click events.

        Called when a legend item is clicked. The default Plotly behavior
        (hiding the trace) will still occur unless prevented via JavaScript.

        Args:
            callback: Function to call with parsed PlotlyLegendClickEvent.
            throttle: Minimum time between event occurrences (seconds).

        Returns:
            Self for method chaining.
        """

        def handler(event):
            parsed = PlotlyLegendClickEvent.from_event_args(event.args)
            callback(parsed)

        # Only request simple properties to avoid circular reference errors
        # (data, fullData, layout contain circular refs that can't be serialized)
        self._plot.on(
            "plotly_legendclick",
            handler,
            args=["curveNumber", "expandedIndex"],
            throttle=throttle,
        )
        return self

    def on_legend_double_click(
        self,
        callback: Callable[[PlotlyLegendClickEvent], None],
        throttle: float = 0.0,
    ) -> "PlotlyEventHandler":
        """Register a callback for legend double-click events.

        Called when a legend item is double-clicked. The default Plotly behavior
        (isolating the trace) will still occur unless prevented via JavaScript.

        Args:
            callback: Function to call with parsed PlotlyLegendClickEvent.
            throttle: Minimum time between event occurrences (seconds).

        Returns:
            Self for method chaining.
        """

        def handler(event):
            parsed = PlotlyLegendClickEvent.from_event_args(event.args)
            callback(parsed)

        # Only request simple properties to avoid circular reference errors
        self._plot.on(
            "plotly_legenddoubleclick",
            handler,
            args=["curveNumber", "expandedIndex"],
            throttle=throttle,
        )
        return self
