from nicegui import ui
from random_username.generate import generate_username

# props is for quesar properties, classes is for tailwind css classes
# props https://quasar.dev/vue-components/button
# class https://tailwindcss.com/docs/font-size
# style direct css


# --- Fixed Header ---
with ui.header(bordered=True, elevated=False).style("background-color: #F9F9F9; height: 40px; padding: 0 20px;"):
    ui.label("Depict AI").classes("text-lg font-bold text-black")
    ui.space()
    with ui.button(icon="account_circle").props("flat color=black"):
        with ui.menu() as menu:
            ui.menu_item("Support")
            ui.menu_item("Subscription")
            ui.separator()
            ui.menu_item("Log out")

# --- Fixed left sidebar ---
with ui.column().classes("fixed left-0 top-10 h-screen w-[70px] bg-gray-100 p-2 items-center shadow-md"):
    with ui.button(icon="folder", on_click=lambda: project_dialog.open()).props("flat color=black"):
        ui.tooltip("Projects")
    with ui.button(icon="import_export", on_click=lambda: import_export.open()).props("flat color=black"):
        ui.tooltip("Import/Export")
    with ui.button(icon="filter_alt", on_click=lambda: drawer_filters.toggle()).props("flat color=black"):
        ui.tooltip("Filters")
    with ui.button(icon="brush", on_click=lambda: drawer_home.toggle()).props("flat color=black"):
        ui.tooltip("Manual Annotation")
    with ui.button(icon="rocket_launch", on_click=lambda: drawer_home.toggle()).props("flat color=black"):
        ui.tooltip("AI Annotation")
    with ui.button(icon="cloud", on_click=lambda: drawer_home.toggle()).props("flat color=black"):
        ui.tooltip("Remote storage")
    with ui.button(icon="analytics", on_click=lambda: drawer_home.toggle()).props("flat color=black"):
        ui.tooltip("Data analytics")

    ui.space()

    with ui.button(icon="settings", on_click=lambda: drawer_settings.toggle()).props("flat color=black"):
        ui.tooltip("Settings")
    ui.button().props("flat color=black")  # TODO FIX empty button for spacing

# --- Main content area (scrollable) ---
with ui.column().classes("ml-[70px] p-4 space-y-4"):
    image_url = "https://picsum.photos/id/377/640/360"
    image_name = "Beautiful Mountains"
    with ui.image(image_url):
        with ui.tooltip(image_name):
            ui.button(icon="check", on_click=lambda: ui.notify("image approved"))
            ui.button(icon="close", on_click=lambda: ui.notify("request change"))
            ui.button(icon="verified", on_click=lambda: ui.notify("request change"))
    for i in range(50):
        ui.label(f"Line {i+1}: Scrollable content here")


# Project
with ui.dialog() as project_dialog, ui.card():
    ui.label("project list")
    for project in range(5):
        with ui.card():
            ui.label(f"Project: {generate_username})")
            ui.button("Open Project")
    ui.button("Close", on_click=project_dialog.close)

# import_export
with ui.dialog() as import_export, ui.card():
    ui.label("Hello world!")
    ui.button("Close", on_click=import_export.close)


# filters
drawer_filters = ui.drawer(side="right", value=False, bordered=True)
with drawer_filters:
    radio1 = ui.radio([1, 2, 3], value=1).props("inline")
    radio2 = ui.radio({1: "A", 2: "B", 3: "C"}).props("inline").bind_value(radio1, "value")
    slider = ui.slider(min=0, max=100, value=50)
    ui.label().bind_text_from(slider, "value")


# settings
drawer_settings = ui.drawer(side="right", value=False, bordered=True)
with drawer_settings:
    ui.label("Settings")
    ui.checkbox("Enable notifications")
    ui.select(["Low", "Medium", "High"], label="Privacy Level")

ui.run()
