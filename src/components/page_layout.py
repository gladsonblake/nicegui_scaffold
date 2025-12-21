"""Page layout component for NiceGUI applications.

Provides a reusable layout structure with optional headers, footers, and drawers.
"""

from functools import wraps
from typing import Callable, Optional

from nicegui import app, ui


class PageLayout:
    """A reusable page layout decorator with optional header, footer, and drawers.

    Uses Quasar-style layout with drawers that auto-show on desktop and
    toggle buttons in the header.

    Example:
        ```python
        @PageLayout(
            header_content=lambda: ui.label("My App"),
            left_drawer_content=PageLayout.render_navigation,
        )
        def my_page(layout):
            ui.label("Page content here")
        ```
    """

    def __init__(
        self,
        header_content: Optional[Callable[[], None]] = None,
        footer_content: Optional[Callable[[], None]] = None,
        left_drawer_content: Optional[Callable[[], None]] = None,
        right_drawer_content: Optional[Callable[[], None]] = None,
        header_elevated: bool = True,
        primary_color: str = "#22c55e",
        secondary_color: str = "#166534",
        accent_color: str = "#bef264",
        positive_color: str = "#22c55e",
        negative_color: str = "#c10015",
        info_color: str = "#31ccec",
        warning_color: str = "#f2c037",
        dark_color: str = "#1d1d1d",
        dark_page_color: str = "#121212",
    ):
        """Initialize the page layout."""
        self.header_content = header_content
        self.footer_content = footer_content
        self.left_drawer_content = left_drawer_content
        self.right_drawer_content = right_drawer_content
        self.header_elevated = header_elevated
        self.primary_color = primary_color
        self.secondary_color = secondary_color
        self.accent_color = accent_color
        self.positive_color = positive_color
        self.negative_color = negative_color
        self.info_color = info_color
        self.warning_color = warning_color
        self.dark_color = dark_color
        self.dark_page_color = dark_page_color

        self.left_drawer: Optional[ui.left_drawer] = None
        self.right_drawer: Optional[ui.right_drawer] = None

    @staticmethod
    def _nav_item(icon: str, label: str, path: str) -> None:
        """Render a single navigation item."""
        with ui.link(target=path).classes("w-full no-underline"):
            with ui.row(align_items="center").classes(
                "gap-3 px-4 py-3 w-full rounded-lg "
                "hover:bg-gray-100 dark:hover:bg-gray-700 "
                "hover:shadow-sm cursor-pointer group "
                "justify-center"
            ):
                ui.icon(icon).classes("text-gray-600 dark:text-gray-400 group-hover:text-primary").props("size=sm")
                ui.label(label).classes("text-gray-700 dark:text-gray-300 font-medium group-hover:text-primary")

    @staticmethod
    def render_navigation() -> None:
        """Render navigation menu in left drawer."""
        nav_items = [
            ("Home", "/", "home"),
            ("Drawers", "/drawers-only", "menu"),
        ]

        ui.label("Navigation").classes("text-lg font-bold mb-4")

        ui.separator()

        for label, path, icon in nav_items:
            PageLayout._nav_item(icon, label, path)

        # Dark mode toggle at bottom
        with ui.column().classes("mt-auto w-full"):
            ui.separator().classes("my-2")
            dark_mode_value = app.storage.user.get("dark_mode", True)
            dark = ui.dark_mode(value=dark_mode_value)

            def save_dark_mode(e):
                app.storage.user["dark_mode"] = e.value

            with ui.row().classes("items-center gap-3 px-3 py-2 w-full"):
                ui.switch("Dark mode", value=dark.value).bind_value(dark).on_value_change(save_dark_mode)

    def _setup_layout(self) -> None:
        """Set up the page layout components."""
        ui.colors(
            primary=self.primary_color,
            secondary=self.secondary_color,
            accent=self.accent_color,
            positive=self.positive_color,
            dark=self.dark_color,
            dark_page=self.dark_page_color,
            negative=self.negative_color,
            info=self.info_color,
            warning=self.warning_color,
        )

        # Create drawers with value=None for Quasar's show-if-above behavior
        if self.left_drawer_content:
            self.left_drawer = ui.left_drawer(value=None, top_corner=True, bottom_corner=True).props(
                "bordered width=200"
            )
            with self.left_drawer:
                with ui.column().classes("flex flex-col h-full gap-1 w-full pt-4"):
                    self.left_drawer_content()

        if self.right_drawer_content:
            self.right_drawer = ui.right_drawer(value=None, top_corner=True, bottom_corner=True).props(
                "bordered width=200"
            )
            with self.right_drawer:
                with ui.column().classes("p-4 gap-2 w-full"):
                    self.right_drawer_content()

        # Create header with toggle buttons
        with ui.header(elevated=self.header_elevated).classes("items-center justify-between"):
            # Left toggle button
            if self.left_drawer:
                ui.button(icon="menu", on_click=self.left_drawer.toggle).props("flat dense round color=white")

            # Header content
            if self.header_content:
                self.header_content()

            # Right toggle button
            if self.right_drawer:
                ui.button(icon="menu", on_click=self.right_drawer.toggle).props("flat dense round color=white")

        # Create footer if content is provided
        if self.footer_content:
            with ui.footer().classes("bg-primary text-white px-4 py-2"):
                with ui.row().classes("items-center justify-center w-full"):
                    self.footer_content()

    def __call__(self, func: Callable) -> Callable:
        """Decorate a page function with this layout."""

        @wraps(func)
        def wrapper(*args, **kwargs):
            self._setup_layout()
            return func(self, *args, **kwargs)

        wrapper.layout = self
        return wrapper
