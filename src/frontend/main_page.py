from nicegui import ui

from src.frontend.pages.admin import read_user_data
from src.frontend.pages.ai_annotation import ai_annotation
from src.frontend.pages.filters import annotation_filters
from src.frontend.pages.import_export import image_import
from src.frontend.pages.infinit_scroll import load_random_img_infinit
from src.frontend.pages.projects import create_project, fetch_project, join_project
from src.frontend.pages.settings import settings_page
from src.frontend.utils.session_storage import store


@ui.page("/")  # main_page
async def profile_page():
    # --- Header ---
    with ui.header(bordered=True, elevated=False).style("background-color: #F9F9F9; height: 40px; padding: 0 20px;"):
        ui.label("Depict AI").classes("text-lg font-bold text-black")
        ui.space()
        with ui.button(icon="account_circle").props("flat color=black"):
            with ui.menu() as menu:
                ui.menu_item("Support")
                ui.menu_item("Subscription")
                ui.separator()
                ui.menu_item("Log out")

    # --- icons sidebar ---
    with ui.column().classes("fixed left-0 top-10 h-screen w-[70px] bg-gray-100 p-2 items-center shadow-md"):
        with ui.button(icon="folder", on_click=lambda: dialog_project.open()).props("flat color=black"):
            ui.tooltip("Projects")
        with ui.button(icon="import_export", on_click=lambda: drawer_import_export.toggle()).props("flat color=black"):
            ui.tooltip("Import/Export")
        with ui.button(icon="filter_alt", on_click=lambda: drawer_annotation_filters.toggle()).props(
            "flat color=black"
        ):
            ui.tooltip("Filters")
        with ui.button(icon="brush").props("flat color=black"):
            ui.tooltip("Manual Annotation")
        with ui.button(icon="rocket_launch", on_click=lambda: drawer_ai_annotation.toggle()).props("flat color=black"):
            ui.tooltip("AI Annotation")
        with ui.button(icon="cloud").props("flat color=black"):
            ui.tooltip("Remote storage")
        with ui.button(icon="analytics").props("flat color=black"):
            ui.tooltip("Data analytics")
        with ui.button(icon="insights").props("flat color=black"):
            ui.tooltip("ML Tools")  # TODO link to ML tools page fp fn analystics

        ui.space()

        with ui.button(icon="settings", on_click=lambda: dialog_settings.open()).props("flat color=black"):
            ui.tooltip("Settings")
        with ui.button(icon="admin_panel_settings", on_click=lambda: dialog_admin.open()).props("flat color=black"):
            ui.tooltip("admin page")

        ui.button().props("flat color=black")  # TODO FIX empty button for spacing

    # --- Drawers and dialogs ---
    # TODO move them to pages or components
    # project
    with ui.dialog() as dialog_project, ui.card():
        ui.label("project List").classes("text-lg font-bold")
        with ui.row():
            ui.button("create project", on_click=create_project)
            ui.button("join project", on_click=join_project)
        ui.label("All your projects")
        try:
            await fetch_project()
        except Exception as e:
            ui.label(f"Error: {e}")

    # settings
    with ui.dialog() as dialog_settings, ui.card():
        ui.label("Settings").classes("text-lg font-bold")
        ui.label("settings content goes here...")
        settings_page()

    # admin
    with ui.dialog() as dialog_admin, ui.card():
        ui.button("view all users", on_click=read_user_data)
        # ui.button("view all project", on_click=read_project_data)

    # import export
    drawer_import_export = ui.drawer(side="right", value=False, bordered=True)
    with drawer_import_export:
        image_import()

    # annotation filters
    drawer_annotation_filters = ui.drawer(side="right", value=False, bordered=True)
    with drawer_annotation_filters:
        annotation_filters()

    # ai annotation
    drawer_ai_annotation = ui.drawer(side="right", value=False, bordered=True)
    with drawer_ai_annotation:
        ai_annotation()

    # --- Main content area (scrollable) ---
    with ui.column().classes("ml-[70px] p-4 space-y-4"):
        if not store.project_id:
            dialog_project.open()
            ui.label("No project selected").classes("text-3xl font-bold")
            ui.label("Please select, join or create a project to continue.").classes("text-xl ")
        else:
            await load_random_img_infinit()


# TODO remove ( just for experimentation)
store.user_id = 1
ui.run()