from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class CommentCreate(BaseModel):
    text: str
    post_id: int
    parent_id: Optional[int] = None


class CommentUpdate(BaseModel):
    text: Optional[str] = None

class Reply(BaseModel):
    id: int
    text: str
    created_at: datetime
    is_blocked: bool
    author_id: int
    post_id: int
    parent_id: Optional[int] = None

    class Config:
        from_attributes = True

class CommentResponse(BaseModel):
    id: int
    text: str
    created_at: datetime
    is_blocked: bool
    author_id: int
    post_id: int
    parent_id: Optional[int] = None
    replies: Optional[List[Reply]] = []

    class Config:
        from_attributes = True