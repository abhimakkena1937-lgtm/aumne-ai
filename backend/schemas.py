
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


PostStatus = Literal["draft", "flagged", "approved", "published"]


class PostCreate(BaseModel):
    title: str = Field(
        min_length=1,
        max_length=200,
        description="Title of the blog post",
    )

    content: str = Field(
        min_length=1,
        max_length=10000,
        description="Content submitted for moderation",
    )


class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    status: PostStatus
    flagged_reasons: list[str] | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

