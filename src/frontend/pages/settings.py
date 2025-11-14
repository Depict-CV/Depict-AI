from nicegui import ui

from src.frontend.utils.session_storage import store


def settings_page():
    slider = ui.slider(min=5, max=100, value=42)
    ui.label().bind_text_from(slider, "value")

    store.settings_image_size = slider.value
