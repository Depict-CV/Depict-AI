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


class ProjectUserLink(SQLModel, table=True):
    project_id: int | None = Field(default=None, foreign_key="project.id", primary_key=True)
    user_id: int | None = Field(default=None, foreign_key="user.id", primary_key=True)


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    email: str = Field(index=True, unique=True)
    hashed_password: str | None = Field(default=None, nullable=True)  # Nullable for OAuth users
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

    # Relation many-to-many
    users: List[User] = Relationship(back_populates="projects", link_model=ProjectUserLink)


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
    # frame_position: int | None = Field(default=None, nullable=True) # for video & frames
    # box coordinates
    # x1:int | None
    # y1:int | None
    # x2:int | None
    # y2:int | None
    # keypoints coordinates
    # keypoints_nodes: List[Tuple[int, int]] # todo
    # keypoints_edges:List[Tuple[int, int]] # todo
    # mask
    # mask_path: str  # todo path to local server only
    # mask_segments:List[Tuple[int, int]] # todo
    # label and description
    label: str | None = Field(default=None, nullable=True)
    # description: str | None = Field(default=None, nullable=True)
    # other info
    annotation_score: float | None = Field(default=None, nullable=True)
    creation_date: datetime | None = Field(default=None, nullable=True)
    # last_updated_date: datetime | None  = Field(default=None, nullable=True)

    data_id: int | None = Field(default=None, foreign_key="data.id")
    author_id: int | None = Field(default=None, foreign_key="user.id")
    project_id: int | None = Field(default=None, foreign_key="project.id")


# TODO add organization table ( a comapny can only its project not form other company)
# TODO maybe add the list of labels that exist in the project
