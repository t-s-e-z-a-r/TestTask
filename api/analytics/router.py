from fastapi import APIRouter, Depends

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, case

from database.config import get_async_session
from database.models import Comment

from datetime import date

from typing import List

from .schemas import CommentBreakdown

analytics_router = APIRouter()


@analytics_router.get("/comments", response_model=List[CommentBreakdown])
async def comments_daily_breakdown(
    date_from: date, date_to: date, db: AsyncSession = Depends(get_async_session)
):
    query = (
        select(
            func.date(Comment.created_at).label("date"),
            func.count(Comment.id).label("total_comments"),
            func.sum(case((Comment.is_blocked == True, 1), else_=0)).label(
                "blocked_comments"
            ),
        )
        .where(Comment.created_at >= date_from, Comment.created_at <= date_to)
        .group_by(func.date(Comment.created_at))
        .order_by(func.date(Comment.created_at))
    )

    result = await db.execute(query)
    breakdown = result.fetchall()

    return [
        CommentBreakdown(
            date=row.date,
            total_comments=row.total_comments,
            blocked_comments=row.blocked_comments,
        )
        for row in breakdown
    ]
