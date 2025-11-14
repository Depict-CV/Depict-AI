from datetime import datetime
from pathlib import Path

import httpx
from nicegui import ui

from config import config
from src.frontend.utils.session_storage import store
from src.frontend.utils.tags import TAG_IMAGE

API_URL = config.API_URL


async def on_file_uploaded(directory_path: str):
    """Called once per uploaded file"""
    print(directory_path)
    directory_path = Path(directory_path)
    image_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff", ".webp"}
    image_paths = [str(p) for p in directory_path.rglob("*") if p.suffix.lower() in image_extensions]
    print(f"Found {len(image_paths)} images:")
    async with httpx.AsyncClient() as client:
        data_batch = [
            {
                "location": f,
                "user_id": store.user_id,
                "project_id": store.project_id,
                "type": TAG_IMAGE,
                "creation_date": datetime.now().strftime("%Y-%m-%d_%Hh:%Mm"),
            }
            for f in image_paths
        ]
        response = await client.post(f"{API_URL}/data/add_batch", json=data_batch)
        if response.status_code == 200:
            data = response.json()
            ui.notify(
                f"image added : {data["created"]}, image skipped : {data["skipped"]} ",
                color="positive",
            )
            ui.notify("Uploaded and added images to project", color="positive")
        else:
            ui.notify(f"Failed to add images to project: {response.text}", color="negative")


def image_import():
    with ui.column().classes("items-center p-4 gap-4"):
        ui.label("📁 Select a folder containing images").classes("text-xl font-semibold")
        directory_path = ui.input("give direcrotory path all images in the sub directory will be automatically").props(
            "outlined"
        )
        ui.button("Import", on_click=lambda e: on_file_uploaded(directory_path.value)).props("outlined")

    # select a
