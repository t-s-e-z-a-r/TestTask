import asyncio

from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from database.config import get_async_session
from database.models import Comment, User

from typing import List, Optional

from auth.services import get_current_user
from celery_app import create_auto_response_comment, is_text_toxic
from .schemas import CommentCreate, CommentUpdate, CommentResponse


comment_router = APIRouter()


@comment_router.post("/", response_model=CommentResponse)
async def create_comment(
    comment: CommentCreate,
    db: AsyncSession = Depends(get_async_session),
    user_id: int = Depends(get_current_user),
):
    if comment.parent_id:
        parent_comment = await db.get(Comment, comment.parent_id)
        if not parent_comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parent comment not found",
            )
        if parent_comment.post_id != comment.post_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Post ID of the reply does not match the parent comment's post ID",
            )

    new_comment = Comment(
        text=comment.text,
        post_id=comment.post_id,
        author_id=user_id,
        parent_id=comment.parent_id,
    )
    new_comment.is_blocked = await asyncio.to_thread(is_text_toxic, comment.text)
    db.add(new_comment)
    await db.commit()
    await db.refresh(new_comment, attribute_names=["replies"])
    if new_comment.is_blocked:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Your comment has been blocked because of toxic content.",
        )
    if not comment.parent_id:
        user = await db.get(User, user_id)
        if user.auto_respond:
            # create_auto_response_comment.apply_async((new_comment.id,), countdown=user.respond_time * 60)
            create_auto_response_comment.apply_async(
                (new_comment.id,), countdown=user.respond_time
            )
    return new_comment


@comment_router.get("/", response_model=List[CommentResponse])
async def get_comments(
    post_id: Optional[int] = None,
    author_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_async_session),
):
    query = (
        select(Comment)
        .filter(Comment.parent_id == None)
        .options(selectinload(Comment.replies))
    )
    if post_id is not None:
        query = query.filter(Comment.post_id == post_id)
    if author_id is not None:
        query = query.filter(Comment.author_id == author_id)
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    comments = result.scalars().all()

    return comments


@comment_router.get("/{comment_id}", response_model=CommentResponse)
async def get_comment(comment_id: int, db: AsyncSession = Depends(get_async_session)):
    query = (
        select(Comment)
        .options(selectinload(Comment.replies))
        .filter(Comment.id == comment_id)
    )
    result = await db.execute(query)
    comment = result.scalars().first()
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found"
        )
    return comment


@comment_router.put("/{comment_id}", response_model=CommentResponse)
async def update_comment(
    comment_id: int,
    comment: CommentUpdate,
    db: AsyncSession = Depends(get_async_session),
    user_id: int = Depends(get_current_user),
):
    result = await db.execute(select(Comment).filter(Comment.id == comment_id))
    existing_comment = result.scalars().first()
    if not existing_comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found"
        )
    if existing_comment.author_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this comment",
        )

    if comment.text is not None:
        existing_comment.text = comment.text
    existing_comment.is_blocked = await asyncio.to_thread(is_text_toxic, comment.text)
    db.add(existing_comment)
    await db.commit()
    await db.refresh(existing_comment, attribute_names=["replies"])
    if existing_comment.is_blocked:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Your comment has been blocked because of toxic content.",
        )
    return existing_comment


@comment_router.delete("/{comment_id}", response_model=dict)
async def delete_comment(
    comment_id: int,
    db: AsyncSession = Depends(get_async_session),
    user_id: int = Depends(get_current_user),
):
    result = await db.execute(select(Comment).filter(Comment.id == comment_id))
    existing_comment = result.scalars().first()
    if not existing_comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found"
        )
    if existing_comment.author_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this comment",
        )

    await db.delete(existing_comment)
    await db.commit()
    return {"msg": "Comment successfully deleted"}
