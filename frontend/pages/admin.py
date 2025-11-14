from nicegui import ui

from config import config
from frontend.utils.session_storage import store

API_URL = config.API_URL


async def read_user_data():
    ui.label("Project Name")
    ui.label(f"user_id: {store.user_id}")
    ui.label(f"project_id: {store.project_id}")
    ui.label(f"data_id: {store.data_id}")
    ui.label(f"annotation_id: {store.annotation_id}")
    ui.label(f"settings_image_size: {store.settings_image_size}")
