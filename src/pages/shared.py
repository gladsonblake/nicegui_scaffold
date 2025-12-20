from nicegui import ui


def _render_settings() -> None:
    """Render settings panel in right drawer."""
    ui.label("Settings").classes("text-lg font-bold mb-4")

    with ui.column().classes("gap-2"):
        ui.label("Notifications").classes("font-semibold")
        ui.checkbox("Email notifications", value=True)
        ui.checkbox("Push notifications", value=False)

        ui.separator()

        ui.button("Save Settings", icon="save").classes("mt-4")
