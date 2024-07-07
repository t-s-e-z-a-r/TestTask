from pydantic import BaseModel
from datetime import date


class DateRange(BaseModel):
    date_from: date
    date_to: date


class CommentBreakdown(BaseModel):
    date: date
    total_comments: int
    blocked_comments: int
