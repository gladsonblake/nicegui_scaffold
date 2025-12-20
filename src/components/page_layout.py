"""Page layout component for NiceGUI applications.

Provides a reusable layout structure with optional headers, footers, and drawers.
"""

from functools import wraps
from typing import Callable, Optional

from nicegui import app, ui


class PageLayout:
    """A reusable page layout decorator with optional header, footer, and drawers.

    This component provides a consistent layout structure for NiceGUI pages with
    modern styling and flexible configuration options.

    Example:
        ```python
        @PageLayout(
            header_content=lambda: ui.label("My App"),
            footer_content=lambda: ui.label("Footer"),
            left_drawer_content=PageLayout.render_navigation,
        )
        def my_page():
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
        left_drawer_fixed: bool = True,
        right_drawer_fixed: bool = True,
    ):
        """Initialize the page layout.

        Args:
            header_content: Optional function to render header content.
            footer_content: Optional function to render footer content.
            left_drawer_content: Optional function to render left drawer content.
            right_drawer_content: Optional function to render right drawer content.
            header_elevated: Whether the header should have elevation/shadow.
            primary_color: Primary theme color.
            secondary_color: Secondary theme color.
            accent_color: Accent theme color.
            positive_color: Positive/success theme color.
            negative_color: Negative/error theme color.
            info_color: Info theme color.
            warning_color: Warning theme color.
            dark_color: Dark theme color.
            dark_page_color: Dark page background color.
            left_drawer_fixed: Whether the left drawer is fixed or scrolls with content.
            right_drawer_fixed: Whether the right drawer is fixed or scrolls with content.
        """
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
        self.left_drawer_fixed = left_drawer_fixed
        self.right_drawer_fixed = right_drawer_fixed

        self.left_drawer = None
        self.right_drawer = None
        self.header = None

    @staticmethod
    def _nav_item(icon: str, label: str, path: str, collapsed: bool) -> None:
        """Render a single navigation item."""
        with ui.link(target=path).classes("w-full no-underline"):
            if collapsed:
                # Centered icon-only for collapsed state
                with ui.row().classes(
                    "justify-center items-center py-2 rounded-lg w-full hover:bg-primary/10 transition-colors cursor-pointer"
                ):
                    ui.icon(icon).classes("text-primary text-xl")
            else:
                # Icon + label for expanded state
                with ui.row().classes(
                    "items-center gap-3 px-3 py-2 rounded-lg w-full hover:bg-primary/10 transition-colors cursor-pointer"
                ):
                    ui.icon(icon).classes("text-primary text-xl")
                    ui.label(label).classes("text-gray-700 dark:text-gray-300")

    @staticmethod
    def render_navigation(drawer: Optional["ui.left_drawer"] = None) -> None:
        """Render navigation menu in left drawer with collapsible support."""
        # Get collapsed state from storage, default to False (expanded)
        collapsed = app.storage.user.get("sidebar_collapsed", False)

        # Toggle button callback
        def toggle_sidebar():
            new_state = not app.storage.user.get("sidebar_collapsed", False)
            app.storage.user["sidebar_collapsed"] = new_state
            ui.navigate.reload()

        # Toggle button - centered when collapsed, right-aligned when expanded
        toggle_icon = "chevron_right" if collapsed else "chevron_left"
        justify_class = "justify-center" if collapsed else "justify-end"
        with ui.row().classes(f"w-full {justify_class} px-1 pb-2"):
            ui.button(
                icon=toggle_icon,
                on_click=toggle_sidebar,
            ).props("flat round dense").classes("text-gray-500 hover:text-primary")

        nav_items = [
            ("Home", "/", "home"),
            ("Drawers", "/drawers-only", "menu"),
        ]

        # Navigation header (only show when expanded)
        if not collapsed:
            ui.label("Navigation").classes("text-sm font-semibold text-gray-500 dark:text-gray-400 px-3 pb-1")

        # Navigation items
        for label, path, icon in nav_items:
            PageLayout._nav_item(icon, label, path, collapsed)

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

        # Create left drawer if content is provided
        if self.left_drawer_content:
            # Get collapsed state from storage for dynamic width
            collapsed = app.storage.user.get("sidebar_collapsed", False)
            drawer_width = 56 if collapsed else 200

            self.left_drawer = ui.left_drawer(
                fixed=self.left_drawer_fixed,
                top_corner=True,
                bottom_corner=True,
            ).props(f"bordered width={drawer_width}")

            with self.left_drawer:
                with ui.column().classes("gap-1 w-full h-full pt-2"):
                    self.left_drawer_content()

        # Create right drawer if content is provided
        if self.right_drawer_content:
            self.right_drawer = ui.right_drawer(
                fixed=self.right_drawer_fixed,
                top_corner=True,
                bottom_corner=True,
            ).props("bordered width=200")

            with self.right_drawer:
                with ui.column().classes("p-4 gap-2 w-full"):
                    self.right_drawer_content()

        # Create header if content is provided
        if self.header_content:
            self.header = ui.header(
                elevated=self.header_elevated,
            ).classes("bg-primary text-white items-center justify-between px-4 py-2")

            with self.header:
                with ui.row().classes("items-center gap-4 flex-1"):
                    # Add drawer toggle buttons if drawers are present
                    if self.left_drawer:
                        ui.button(
                            icon="menu",
                            on_click=lambda: self.left_drawer.toggle(),
                        ).props("flat color=white")

                    # Render header content
                    self.header_content()

                # Add right drawer toggle button if present
                if self.right_drawer:
                    ui.button(
                        icon="menu",
                        on_click=lambda: self.right_drawer.toggle(),
                    ).props("flat color=white")

        # Create footer if content is provided
        if self.footer_content:
            with ui.footer().classes("bg-primary text-white px-4 py-2"):
                with ui.row().classes("items-center justify-center w-full"):
                    self.footer_content()

    def __call__(self, func: Callable) -> Callable:
        """Decorate a page function with this layout.

        Args:
            func: The page function to wrap with the layout.

        Returns:
            The wrapped function that renders the layout and page content.
        """

        @wraps(func)
        def wrapper(*args, **kwargs):
            self._setup_layout()
            return func(self, *args, **kwargs)

        # Expose drawer references on the wrapper for external access
        wrapper.layout = self

        return wrapper
