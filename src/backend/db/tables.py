from datetime import datetime
from enum import Enum
from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel


class PermissionEnum(str, Enum):
    VIEW_ONLY = "view only"
    EDIT = "edit"
    EDIT_DELETE = "edit & delete"
    CAN_CERTIFY = "can certify"


class DataTypeEnum(str, Enum):
    IMAGE = "image"
    FRAMES = "frames"
    VIDEO = "video"


class AnnotationStatus(str, Enum):
    TO_REVIEW = "to review"
    HUMAN_ANNOTATION = "human annotation"
    ML_ANNOTATION = "ml annotation"
    REJECTED = "rejected"
    CERTIFIED = "certified"


class AnnotationHistoryStatus(str, Enum):
    HISTORY = "history"
    CURRENT = "current"


class ProjectStatus(str, Enum):
    ACTIVE = "active"
    DELETED = "deleted"
    ARCHIVED = "archived"


class ProjectUserLink(SQLModel, table=True):
    project_id: int | None = Field(default=None, foreign_key="project.id", primary_key=True)
    user_id: int | None = Field(default=None, foreign_key="user.id", primary_key=True)


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    email: str = Field(index=True, unique=True)
    permission: PermissionEnum

    # OAuth2 fields (Clerk, Google, Microsoft, GitHub)
    oauth_provider: str | None = Field(default=None, nullable=True)  # "clerk", "google", "microsoft", "github"
    oauth_id: str | None = Field(default=None, nullable=True)  # Provider's user ID

    data: List["Data"] = Relationship(back_populates="author")
    # Relation many-to-many
    projects: List["Project"] = Relationship(back_populates="users", link_model=ProjectUserLink)


class Project(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    description: str | None = Field(default=None, nullable=True)
    owner_id: int | None = Field(default=None, foreign_key="user.id")
    created_at: datetime | None = Field(default=None, nullable=True)
    status: ProjectStatus = Field(default=ProjectStatus.ACTIVE)

    # Relation many-to-many
    users: List[User] = Relationship(back_populates="projects", link_model=ProjectUserLink)


class MinIOConfig(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    project_id: int = Field(foreign_key="project.id", unique=True, index=True)
    endpoint: str
    bucket_name: str
    access_key: str
    secret_key: str  # TODO: Encrypt this field
    use_ssl: bool = Field(default=False)
    last_sync: datetime | None = Field(default=None, nullable=True)

    project: Optional["Project"] = Relationship()


class Data(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    type: DataTypeEnum
    location: str  # todo  path server or url or api
    author_id: int | None = Field(default=None, foreign_key="user.id")
    creation_date: datetime | None = Field(default=None, nullable=True)
    project_id: int | None = Field(foreign_key="project.id")

    author: Optional[User] = Relationship(back_populates="data")
    project: Optional[Project] = Relationship()


class Annotation(SQLModel, table=True):
    """
    annotation could be the full image, or many annotations  like boxes in the image
    by default the whole image is an annotation
    """

    id: int | None = Field(default=None, primary_key=True)
    status: AnnotationStatus
    history_status: AnnotationHistoryStatus = Field(default=AnnotationHistoryStatus.CURRENT)
    # frame_position: int | None = Field(default=None, nullable=True) # for video & frames
    # box coordinates
    x1: int | None = Field(default=None, nullable=True)
    y1: int | None = Field(default=None, nullable=True)
    x2: int | None = Field(default=None, nullable=True)
    y2: int | None = Field(default=None, nullable=True)
    # keypoints coordinates (store as JSON string)
    # Format: {"nodes": [{"x": 100, "y": 200, "index": 0, "body_part": "nose"}, ...], "edges": [[0, 1], [1, 2], ...]}
    keypoints: str | None = Field(default=None, nullable=True)
    # mask segments (store as JSON string)
    # Format: [[x1, y1, x2, y2, ...], [x1, y1, x2, y2, ...]] - array of polygon point arrays
    mask_segments: str | None = Field(default=None, nullable=True)
    # polygon coordinates (store as JSON string)
    # Format: [x1, y1, x2, y2, ...] - flat array of polygon points
    polygon: str | None = Field(default=None, nullable=True)
    # label and description
    label: str | None = Field(default=None, nullable=True)
    description: str | None = Field(default=None, nullable=True)
    # other info
    annotation_score: float | None = Field(default=None, nullable=True)
    creation_date: datetime | None = Field(default=None, nullable=True)
    # annotation colud be another image as well

    data_id: int | None = Field(default=None, foreign_key="data.id")
    author_id: int | None = Field(default=None, foreign_key="user.id")
    project_id: int | None = Field(default=None, foreign_key="project.id")


# TODO maybe add the list of labels that exist in the project
