# TODO check redis for session storage
class Store:
    user_id: int | None = None
    project_id: int | None = None
    data_id: int | None = None
    annotation_id: int | None = None

    settings_image_size: int = 32  # TODO why it is not 32 by default but the default value at settings_page?


store = Store()
