from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime
from api.comments.schemas import CommentResponse, Reply


class PostCreate(BaseModel):
    title: str
    text: str


class PostUpdate(BaseModel):
    title: Optional[str] = None
    text: Optional[str] = None


class PostResponse(BaseModel):
    id: int
    title: str
    text: str
    created_at: datetime
    is_blocked: bool
    author_id: int
    comments: List[CommentResponse] = []

    class Config(ConfigDict):
        from_attributes = True
