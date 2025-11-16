# TODO check redis for session storage
class Store:
    user_id: int | None = None
    project_id: int | None = None
    data_id: int | None = None
    annotation_id: int | None = None

    settings_image_size: int = 42


store = Store()
