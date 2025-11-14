import httpx
from nicegui import ui

from config import config
from src.frontend.utils.session_storage import store

API_URL = config.API_URL


def run_annotation():
    # get annotation id and image
    if not store.annotation_id:
        with httpx.Client() as client:
            response = client.post(
                f"{API_URL}/annotations/score",
                json={"project_id": store.project_id, "limit": 1, "offset": 0},
            )
            if response.status_code == 200:
                r = response.json()[0]
                store.annotation_id = r["id"]
                store.data_id = r["data_id"]

    annotation_id = store.annotation_id
    data_id = store.data_id

    with httpx.Client() as client:
        response = client.post(f"{API_URL}/data/batch", json={"data_ids": [data_id]})
        if response.status_code == 200:
            image_path = response.json()[0]["location"]

        response = client.get(f"{API_URL}/annotations/{annotation_id}")
        if response.status_code == 200:
            annotation = response.json()
    ui.image(image_path)
    ui.label(f"Annotation : {annotation}")

    with httpx.Client() as client:
        client.patch(
            f"{API_URL}/annotations",
            json={
                "id": int(annotation.get("id")),
                "annotation_score": annotation.get("annotation_score") + config.annotation["view_score"],
            },
        )
