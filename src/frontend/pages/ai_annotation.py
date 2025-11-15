import httpx
from nicegui import ui

from config import config
from src.frontend.utils.session_storage import store
from src.frontend.utils.tags import TAG_ML_ANNOTATION

API_URL = config.API_URL


async def add_ml_annotation():
    async with httpx.AsyncClient() as client:
        # get all images in the project that do not have an annotation yet
        response = await client.get(f"{API_URL}/data/non_labeled", params={"project_id": store.project_id})
        if response.status_code == 200:
            no_label_annotations = response.json()
            for img in no_label_annotations:
                data_path = img["location"]
                data_id = img["id"]
                project_id = img["project_id"]
                response = await client.post(f"{API_URL}/infer/resnet50", json={"image_path": str(data_path)})
                if response.status_code == 200:
                    ml_annotation = response.json()
                    annotation_json = {
                        "data_id": data_id,
                        "author_id": store.user_id,
                        "project_id": project_id,
                        "status": TAG_ML_ANNOTATION,
                        "annotation_score": 0.0,
                        "label": ml_annotation["class_name"],
                    }
                    response = await client.post(f"{API_URL}/annotations/", json=annotation_json)
                    if response.status_code == 200:
                        ui.notify(
                            f"Created default annotation for {data_path}",
                            color="positive",
                        )
                    else:
                        ui.notify(
                            f"Failed to create annotation for {data_path}: {response.text}",
                            color="negative",
                        )
        else:
            ui.notify(
                f"Failed to fetch images without annotations: {response.text}",
                color="negative",
            )


def ai_annotation():
    ui.label("🤖 AI Annotations: all not annotated images will get a predicted ML annotation").classes(
        "text-xl font-semibold"
    )
    ui.button("add ml predicted annotation", on_click=add_ml_annotation).props("outlined")
