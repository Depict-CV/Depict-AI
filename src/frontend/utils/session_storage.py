# TODO check redis for session storage
from src.frontend.utils.tags import TAG_SCORE, TAG_ASC


class Store:
    # session
    user_id: int | None = None
    project_id: int | None = None
    data_id: int | None = None
    annotation_id: int | None = None

    # settings
    settings_image_size: int = 42

    #annoattion filters
    label_selected = []
    sort_by = TAG_SCORE  # 'score' or 'date'
    sort_on = TAG_ASC   # 'asc' or 'desc'

store = Store()
