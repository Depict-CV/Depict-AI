from nicegui import ui

from src.frontend.utils.session_storage import store
from src.frontend.utils.tags import TAG_SCORE, TAG_ASC, TAG_DESC, TAG_DATE


def annotation_filters():
    ui.label("label selection")
    label_selected = ui.input_chips('add labels', value=[])
    def on_change_label():
        store.label_selected = label_selected.value
    label_selected.on('change', on_change_label)

    # sort
    ui.label("sorting options")
    sort_by = ui.select([TAG_SCORE, TAG_DATE], label='Sort by', value=TAG_SCORE)
    sort_on = ui.select([TAG_ASC, TAG_DESC], label='Sort on', value=TAG_ASC)
    def on_change_sort():
        store.sort_by = sort_by.value
        store.sort_on = sort_on.value
    sort_by.on('change', on_change_sort)
    sort_on.on('change', on_change_sort)


    def apply():
        ui.run_javascript('window.location.reload()')

    ui.button('Apply', on_click=apply)

