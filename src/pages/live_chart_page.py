"""Live price chart with real-time updates using simulated data.

Demonstrates NiceGUI's ui.timer for periodic chart updates.
"""

import random
from collections import deque
from datetime import datetime

from nicegui import ui

from components import PageLayout
from utils import PlotlyTheme

# Configuration
UPDATE_INTERVAL = 5.0  # seconds
MAX_DATA_POINTS = 60  # ~5 minutes of data at 5s intervals

# Chart titles
CHART_TITLE = "Simulated Prices - Live"

# Asset configurations (name, starting price, volatility, color)
ASSETS = [
    {"name": "Asset A", "start": 42000.0, "volatility": 0.02, "color": "#22c55e"},  # Green
    {"name": "Asset B", "start": 2800.0, "volatility": 0.025, "color": "#3b82f6"},  # Blue
]


@PageLayout(
    header_content=lambda: ui.label("Live Chart Demo").classes("text-xl font-bold"),
    left_drawer_content=lambda layout: layout.render_navigation(),
)
def _live_chart_page(layout: PageLayout):
    """Live chart page with real-time simulated price updates."""
    # Data storage using deques for efficient rolling window
    timestamps: deque[datetime] = deque(maxlen=MAX_DATA_POINTS)
    # Store prices for each asset
    prices: dict[str, deque[float]] = {asset["name"]: deque(maxlen=MAX_DATA_POINTS) for asset in ASSETS}

    # Track current prices for random walk continuity
    current_prices: dict[str, float] = {asset["name"]: asset["start"] for asset in ASSETS}

    # Initialize theme helper
    theme = PlotlyTheme.from_layout(layout)

    def generate_prices() -> dict[str, float]:
        """Generate next prices for all assets using random walk."""
        result = {}
        for asset in ASSETS:
            name = asset["name"]
            volatility = asset["volatility"]
            # Random percentage change
            change = random.uniform(-volatility, volatility)
            current_prices[name] *= 1 + change
            # Keep price in reasonable bounds (10% - 200% of starting price)
            min_price = asset["start"] * 0.5
            max_price = asset["start"] * 1.5
            current_prices[name] = max(min_price, min(max_price, current_prices[name]))
            result[name] = current_prices[name]
        return result

    def create_figure() -> dict:
        """Create Plotly figure with current data."""
        bg_color, text_color, grid_color = theme.get_colors()

        # Format timestamps for display
        x_data = [t.strftime("%H:%M:%S") for t in timestamps] if timestamps else []

        # Create traces for each asset
        traces = []
        for asset in ASSETS:
            name = asset["name"]
            color = asset["color"]
            y_data = list(prices[name]) if prices[name] else []

            traces.append(
                {
                    "x": x_data,
                    "y": y_data,
                    "type": "scatter",
                    "mode": "lines+markers",
                    "name": name,
                    "line": {"color": color, "width": 2},
                    "marker": {"size": 4},
                    "yaxis": "y" if asset == ASSETS[0] else "y2",
                }
            )

        return {
            "data": traces,
            "layout": {
                "title": {"text": CHART_TITLE, "font": {"size": 14}},
                "margin": {"l": 50, "r": 50, "t": 40, "b": 40},
                "plot_bgcolor": bg_color,
                "paper_bgcolor": bg_color,
                "font": {"color": text_color, "size": 11},
                "legend": {"orientation": "h", "y": -0.15, "x": 0.5, "xanchor": "center"},
                "xaxis": {
                    "title": {"text": "Time", "font": {"size": 12}},
                    "gridcolor": grid_color,
                    "linecolor": text_color,
                    "tickfont": {"size": 10},
                    "automargin": True,
                },
                "yaxis": {
                    "title": {"text": ASSETS[0]["name"], "font": {"size": 11, "color": ASSETS[0]["color"]}},
                    "gridcolor": grid_color,
                    "linecolor": ASSETS[0]["color"],
                    "tickformat": "$,.0f",
                    "tickfont": {"size": 10, "color": ASSETS[0]["color"]},
                    "automargin": True,
                },
                "yaxis2": {
                    "title": {"text": ASSETS[1]["name"], "font": {"size": 11, "color": ASSETS[1]["color"]}},
                    "overlaying": "y",
                    "side": "right",
                    "gridcolor": grid_color,
                    "linecolor": ASSETS[1]["color"],
                    "tickformat": "$,.0f",
                    "tickfont": {"size": 10, "color": ASSETS[1]["color"]},
                    "automargin": True,
                },
                "hovermode": "x unified",
                "autosize": True,
            },
        }

    def update_chart():
        """Generate new price data and update the chart."""
        new_prices = generate_prices()
        now = datetime.now()

        timestamps.append(now)
        for name, price in new_prices.items():
            prices[name].append(price)

        # Update chart
        plot.update_figure(create_figure())

        # Update status display (compact format for mobile)
        price_str = " · ".join(f"{name[:1]}: ${p:,.0f}" for name, p in new_prices.items())
        data_len = len(prices[ASSETS[0]["name"]])
        status_label.set_text(f"{now.strftime('%H:%M:%S')} · {price_str} · {data_len}/{MAX_DATA_POINTS} pts")

    def update_chart_theme(_=None):
        """Update chart when theme changes."""
        plot.update_figure(create_figure())

    # Page content
    with ui.column().classes("w-full gap-3 p-2 sm:p-4"):
        # Header with controls - stacks on mobile, row on desktop
        with ui.column().classes("w-full gap-2 sm:flex-row sm:items-center sm:justify-between"):
            ui.label("Real-time Price Chart").classes("text-xl sm:text-2xl font-bold")

            with ui.row().classes("gap-2 sm:gap-4 items-center flex-wrap"):
                # Auto-update toggle
                timer = ui.timer(UPDATE_INTERVAL, update_chart, active=True)
                ui.switch("Auto-update", value=True).bind_value(timer, "active")

                # Manual refresh button
                ui.button("Refresh", icon="refresh", on_click=update_chart).props("flat dense")

        # Status bar
        status_label = ui.label("Waiting...").classes("text-xs sm:text-sm text-green-500")

        # Main chart - responsive height
        with ui.card().classes("w-full p-1 sm:p-2"):
            plot = ui.plotly(create_figure()).classes("w-full").style("height: clamp(250px, 50vh, 400px)")

        # Info panel
        with ui.expansion("About this demo", icon="info").classes("w-full"):
            ui.markdown(
                """
                This page demonstrates NiceGUI's **event system** with `ui.timer` for real-time updates.

                **Features:**
                - Two simulated price series with independent random walks
                - Dual Y-axes for different price scales
                - Rolling window of last 60 data points (~5 minutes)
                - Theme-aware Plotly chart with dark/light mode support
                - Toggle to pause/resume updates

                **Technical Details:**
                - `ui.timer(5.0, callback)` triggers periodic updates
                - `deque(maxlen=60)` for efficient rolling data storage
                - `plot.update_figure()` for efficient chart updates
                - Each asset has its own volatility and Y-axis
                """
            )

    # Register theme change callback
    layout.on_dark_mode_change(update_chart_theme)
