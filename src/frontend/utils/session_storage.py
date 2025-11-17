# TODO check redis for session storage
from src.frontend.utils.tags import TAG_ASC, TAG_SCORE


class Store:
    def __init__(self):
        # session
        self.user_id = None
        self.project_id = None
        self.data_id = None
        self.annotation_id = None

        # settings
        self.settings_image_size = 42

        # annotation  filters
        self.label_selected = []
        self.sort_by = TAG_SCORE  # 'score' or 'date'
        self.sort_on = TAG_ASC  # 'asc' or 'desc'


store = Store()
