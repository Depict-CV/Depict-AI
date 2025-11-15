from nicegui import ui

from src.frontend.utils.session_storage import store


def settings_page():
    slider = ui.slider(min=5, max=100, value=42)

    def update_store(e):
        store.settings_image_size = slider.value

    slider.on('change', update_store)
    ui.label().bind_text_from(slider, "value")

