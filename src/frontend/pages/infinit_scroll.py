import httpx
from nicegui import ui

from config import config
from src.frontend.components.image import mosaic_image
from src.frontend.pages.manual_annotation import run_annotation
from src.frontend.utils.session_storage import store
from src.frontend.utils.tags import TAG_CERTIFIED, TAG_REJECTED, TAG_TO_REVIEW

API_URL = config.API_URL


async def get_next_batch_annotations(annotation_list, image_offset, batch_size=200):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{API_URL}/annotations/batch",
            json={
                "project_id": store.project_id,
                "limit": batch_size,
                "offset": image_offset,
                "selected_labels" : store.label_selected,
            },
        )
        if response.status_code == 200:
            annotation_list += response.json()
            image_offset = len(annotation_list)
        else:
            ui.notify(f"Failed to fetch annotations: {response.text}", color="negative")
            return [], image_offset
    return annotation_list, image_offset


async def load_random_img_infinit():

    # get imgs
    annotation_list = []
    annotation_list, image_offset = await get_next_batch_annotations(annotation_list, image_offset=0)

    current_annot_idx = 0

    # create a dialog to show zoomed image
    zoom_dialog = ui.dialog()

    # we'll store the currently displayed annotation in this dict so callbacks can access it
    dialog_state = {"annot": None, "img_path": None}

    with zoom_dialog, ui.card().classes("p-4"):
        zoom_img = ui.image().classes("w-96 h-auto shadow-md")
        metadata_label = ui.label().classes("mt-2 text-sm text-gray-600")

        async def patch_annotation_status(
            annot_id: int | None = None,
            status: str | int | None = None,
            annotation_score: float | None = None,
        ):
            if annot_id is None:
                # ensure notify is called while in the UI slot (these callers will be invoked by NiceGUI directly)
                ui.notify("No annotation selected", color="warning")
                return
            payload = {"id": annot_id}
            if status is not None:
                payload["status"] = status
            if annotation_score is not None:
                payload["annotation_score"] = annotation_score  # type: ignore
            try:
                async with httpx.AsyncClient() as client:
                    resp = await client.patch(f"{API_URL}/annotations/", json=payload)
                if resp.status_code in (200, 204):
                    ui.notify("Annotation updated", color="positive")
                else:
                    ui.notify(f"Failed to update annotation: {resp.text}", color="negative")
            except Exception as e:
                # still call ui.notify from the UI slot
                ui.notify(f"Error updating annotation: {e}", color="negative")

        # button callbacks need to be async callback functions so they execute within the NiceGUI slot
        async def on_certify(_event=None):
            annot = dialog_state.get("annot")
            if not isinstance(annot, dict):
                ui.notify("No annotation selected", color="warning")
                return
            id_value = annot.get("id")
            if id_value is None:
                ui.notify("Annotation has no id", color="warning")
                return
            annot_id = int(id_value)
            await patch_annotation_status(
                annot_id=annot_id,
                status=TAG_CERTIFIED,
                annotation_score=annot.get("annotation_score") + config.annotation["certify_score"],
            )
            zoom_dialog.close()

        async def on_to_review(_event=None):
            annot = dialog_state.get("annot")
            if not isinstance(annot, dict):
                ui.notify("No annotation selected", color="warning")
                return
            id_value = annot.get("id")
            if id_value is None:
                ui.notify("Annotation has no id", color="warning")
                return
            annot_id = int(id_value)
            await patch_annotation_status(annot_id=annot_id, status=TAG_TO_REVIEW, annotation_score=0.0)
            zoom_dialog.close()

        async def on_reject(_event=None):
            annot = dialog_state.get("annot")
            if not isinstance(annot, dict):
                ui.notify("No annotation selected", color="warning")
                return
            id_value = annot.get("id")
            if id_value is None:
                ui.notify("Annotation has no id", color="warning")
                return
            annot_id = int(id_value)
            await patch_annotation_status(annot_id=annot_id, status=TAG_REJECTED, annotation_score=0.0)
            zoom_dialog.close()

        def on_annotate():
            run_annotation()

        async def on_use_ml(_event=None):
            await use_ml_prediction_as_annotation(dialog_state, zoom_dialog, metadata_label)

        ui.row().classes("items-center gap-2 mt-3")
        # pass async handlers directly so NiceGUI runs them inside the correct UI slot/context
        ui.button("Certify", on_click=on_certify)
        ui.button("Annotate", on_click=on_annotate)
        ui.button("To review", on_click=on_to_review)
        ui.button("Reject", on_click=on_reject)
        ui.button("use ml prediction as annotation", on_click=on_use_ml)

    async def use_ml_prediction_as_annotation(dialog_state: dict, zoom_dialog, metadata_label):
        """Use the ML prediction to update the current annotation.

        Steps:
        - Validate dialog_state contains an annotation and image path
        - Call the inference API to get prediction
        - Send a PATCH to /annotations adding/updating a field `ml_prediction` or `annotation` depending on backend support
        - Update the metadata_label and notify the user
        """
        # validate state
        annot = dialog_state.get("annot")
        img_path = dialog_state.get("img_path")
        if not isinstance(annot, dict) or annot.get("id") is None:
            ui.notify("No annotation selected to apply ML prediction", color="warning")
            return
        if img_path is None:
            ui.notify("No image path available for prediction", color="warning")
            return

        annot_id = int(annot.get("id"))

        # Always call infer API to obtain the prediction
        prediction = None
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(f"{API_URL}/infer/resnet50", json={"image_path": str(img_path)})
                if resp.status_code == 200:
                    prediction = resp.json()
                else:
                    ui.notify(f"Inference failed: {resp.text}", color="negative")
                    return
        except Exception as e:
            ui.notify(f"Error while requesting prediction: {e}", color="negative")
            return

        # prepare payload - backend might accept 'annotation' or 'ml_prediction'; try both keys
        payload = {"id": annot_id, "ml_prediction": prediction}
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.patch(f"{API_URL}/annotations/", json=payload)
            if resp.status_code in (200, 204):
                ui.notify("Applied ML prediction to annotation", color="positive")
                # update the displayed label with the new prediction
                try:
                    metadata_label.set_text(f"**Annotation:** {annot}  \n**Prediction:** {prediction}")
                except Exception:
                    print("Failed to update metadata label with new prediction")
                zoom_dialog.close()
                return
        except Exception as e:
            ui.notify(f"Failed to apply prediction: {e}", color="negative")

        # If ml_prediction key wasn't accepted, try fallback key
        payload = {"id": annot_id, "annotation": prediction}
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.patch(f"{API_URL}/annotations/", json=payload)
            if resp.status_code in (200, 204):
                ui.notify(
                    "Applied ML prediction to annotation (fallback key)",
                    color="positive",
                )
                try:
                    metadata_label.set_text(f"**Annotation:** {annot}  \n**Prediction:** {prediction}")
                except Exception:
                    print("Failed to update metadata label with new prediction")
                zoom_dialog.close()
                return
            else:
                ui.notify(f"Backend rejected prediction update: {resp.text}", color="negative")
        except Exception as e:
            ui.notify(f"Failed to apply prediction (fallback): {e}", color="negative")

    async def show_zoom(p):
        async with httpx.AsyncClient() as client:
            img_path, annot = p
            # run ml model via API
            store.data_id = annot.get("data_id")
            store.annotation_id = annot.get("id")
            try:
                response = await client.post(f"{API_URL}/infer/resnet50", json={"image_path": str(img_path)})
                prediction = response.json()
            except Exception:
                prediction = None

            # update dialog state so buttons can act on the correct annotation
            dialog_state["annot"] = annot
            dialog_state["img_path"] = img_path

            zoom_img.set_source(str(img_path))
            metadata_label.set_text(f"**Annotation:** {annot}  \n**Prediction:** {prediction}")

            # increment score for being viewed
            try:
                await client.patch(
                    f"{API_URL}/annotations/",
                    json={
                        "id": int(annot.get("id")),
                        "annotation_score": annot.get("annotation_score") + config.annotation["analyse_score"],
                    },
                )
            except Exception:
                print("Failed to increment annotation score on view")

            zoom_dialog.open()

    async def check_scroll():
        nonlocal current_annot_idx
        if await ui.run_javascript("window.pageYOffset >= document.body.offsetHeight - 2 * window.innerHeight"):
            with ui.row().classes("gap-1"):
                annotation_item = annotation_list[current_annot_idx : current_annot_idx + 10]
                data_ids = [item["data_id"] for item in annotation_item]
                # make list of image_id to fetch
                current_annot_idx += 10
                if not data_ids:
                    ui.notify("No more annotations to load", color="negative")
                    return

                async with httpx.AsyncClient() as client:
                    response = await client.post(f"{API_URL}/data/batch", json={"data_ids": data_ids})

                    image_list = response.json()
                    image_list = [item["location"] for item in image_list]

                    # helper to produce a click handler that runs in the UI slot
                    def make_click_handler(p):
                        async def _handler(_event=None):
                            await show_zoom(p)

                        return _handler

                    for img_path, annot in zip(image_list, annotation_item):
                        img = mosaic_image(img_path, annot)
                        img.classes(f"w-{store.settings_image_size} object-cover cursor-pointer").on(
                            "click", make_click_handler((img_path, annot))
                        )
                        # add annotation score 0.1 to the exposed annotation
                        await client.patch(
                            f"{API_URL}/annotations/",
                            json={
                                "id": int(annot.get("id")),
                                "annotation_score": annot.get("annotation_score") + config.annotation["view_score"],
                            },
                        )

    async def check_annotation_list():
        nonlocal annotation_list, image_offset, current_annot_idx
        if current_annot_idx + 50 > len(annotation_list):
            annotation_list, image_offset = await get_next_batch_annotations(annotation_list, image_offset)

    ui.timer(0.1, check_scroll)
    ui.timer(3.0, check_annotation_list)
