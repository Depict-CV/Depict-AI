import httpx
from nicegui import ui

from config import config
from src.frontend.utils.session_storage import store

API_URL = config.API_URL

# TODO to main page add the fact tha the manager can tag annotation so the team can clean them
# TODO make sure that 1 image as 1 annotation
# TODO add notification with all annotation to review
API_URL = config.API_URL

async def create_project():
    with ui.dialog() as dialog:
        with ui.card():
            name = ui.input("name").props("outlined").classes("w-full")
            description = ui.input("description").props("outlined").classes("w-full")
            message = ui.label("")

            async def submit():
                user_data = {
                    "name": name.value,
                    "description": description.value,
                    "owner_id": store.user_id,
                }
                async with httpx.AsyncClient() as client:
                    try:
                        response = await client.post(f"{API_URL}/projects/", json=user_data)
                        if response.status_code == 200 or response.status_code == 201:
                            message.text = "Project added successfully."
                            dialog.close()
                        else:
                            message.text = f"Error: {response.text}"
                    except Exception as e:
                        message.text = f"Exception: {e}"

            ui.button("Submit", on_click=submit)
            ui.button("Cancel", on_click=dialog.close)
    dialog.open()


async def join_project():
    with ui.dialog() as dialog:
        with ui.card():
            project_name = ui.input("project name").props("outlined").classes("w-full")
            message = ui.label("")

            async def submit():
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{API_URL}/projects/fetch",
                        json={"project_name": project_name.value},
                    )

                    if response.status_code == 200:
                        project_id = response.json().get("project_id")
                        try:
                            response = await client.post(f"{API_URL}/projects/{project_id}/users/{store.user_id}")
                            if response.status_code == 200 or response.status_code == 201:
                                message.text = "User added successfully."
                                dialog.close()
                            else:
                                message.text = f"Error: {response.text}"
                        except Exception as e:
                            message.text = f"Exception: {e}"
                    else:
                        ui.notify("Project not found", color="negative")

            ui.button("Submit", on_click=submit)
            ui.button("Cancel", on_click=dialog.close)
    dialog.open()


async def fetch_project():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_URL}/users/{store.user_id}/projects")
        if response.status_code == 200:
            projects = response.json()
            if projects:
                for project in projects:
                    with ui.card():
                        ui.label(f"Project: {project.get('name', 'Unnamed')} (ID: {project.get('id')})")
                        ui.button(
                            "Open Project",
                            on_click=lambda pid=project.get("id"): (setattr(store, "project_id", pid)),
                        )
            else:
                ui.label("No projects found.")
        else:
            ui.label("Failed to fetch projects.")
