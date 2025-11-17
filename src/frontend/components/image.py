import httpx
from nicegui import ui

from src.frontend.pages.admin import API_URL
from src.frontend.utils.tags import TAG_CERTIFIED, TAG_REJECTED, TAG_TO_REVIEW


def mosaic_image(url: str, annot):
    """Creates a styled image with hover overlay buttons and returns the container."""
    container = ui.element("div").classes("relative inline-block group")

    async def _update_annotation_status(tag):
        async with httpx.AsyncClient() as client:
            await client.patch(
                f"{API_URL}/annotations/",
                json={"id": int(annot.get("id")), "status": tag},
            )
        ui.notify("Annotation updated ✅")

    with container:
        with ui.interactive_image(url):
            ui.button(
                icon="verified",
                on_click=lambda e: _update_annotation_status(TAG_CERTIFIED),
            ).props("flat color=white").classes(
                "absolute bottom-0 left-0 m-2 opacity-0 group-hover:opacity-100 transition-opacity"
            )
            ui.button(
                icon="delete",
                on_click=lambda e: _update_annotation_status(TAG_REJECTED),
            ).props("flat color=white").classes(
                "absolute bottom-0 left-12 m-2 opacity-0 group-hover:opacity-100 transition-opacity"
            )
            ui.button(
                icon="policy",
                on_click=lambda e: _update_annotation_status(TAG_TO_REVIEW),
            ).props("flat color=white").classes(
                "absolute bottom-0 left-24 m-2 opacity-0 group-hover:opacity-100 transition-opacity"
            )
    return container


if __name__ == "__main__":
    # Example usage
    mosaic_image("https://picsum.photos/id/1018/800/450", {})

    # You can now reuse it anywhere and even keep a reference
    img1 = mosaic_image("https://picsum.photos/id/1019/800/450", {})
    img2 = mosaic_image("https://picsum.photos/id/1020/800/450", {})

    with ui.row():
        img1
        img2

    ui.run()
