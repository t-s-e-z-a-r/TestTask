from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime


class CommentCreate(BaseModel):
    text: str
    post_id: int
    parent_id: Optional[int] = None


class CommentUpdate(BaseModel):
    text: Optional[str] = None


class CommentResponse(BaseModel):
    id: int
    text: str
    created_at: datetime
    is_blocked: bool
    author_id: int
    post_id: int
    parent_id: Optional[int] = None

    class Config(ConfigDict):
        from_attributes = True
