from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from database.config import get_async_session
from database.models import Post, Comment

from typing import List, Optional

from auth.services import get_current_user
from celery_app import is_text_toxic

from .schemas import PostCreate, PostUpdate, PostResponse

import asyncio

post_router = APIRouter()


@post_router.post("/", response_model=PostResponse)
async def create_post(
    post: PostCreate,
    db: AsyncSession = Depends(get_async_session),
    user_id: int = Depends(get_current_user),
):
    new_post = Post(title=post.title, text=post.text, author_id=user_id)
    if is_text_toxic(f"{post.title} {post.text}"):
        new_post.is_blocked = True
    db.add(new_post)
    await db.commit()
    await db.refresh(new_post, attribute_names=["comments"])
    if new_post.is_blocked:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Your post has been blocked because of toxic content.",
        )
    return new_post


@post_router.get("/", response_model=List[PostResponse])
async def get_posts(
    author_id: int = None,
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_async_session),
):
    query = select(Post)
    if author_id is not None:
        query = query.filter(Post.author_id == author_id)
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    posts = result.scalars().all()
    return posts


@post_router.get("/{post_id}", response_model=PostResponse)
async def get_post(post_id: int, db: AsyncSession = Depends(get_async_session)):
    result = await db.execute(select(Post).filter(Post.id == post_id))
    post = result.scalars().first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )
    return post


@post_router.put("/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: int,
    post: PostUpdate,
    db: AsyncSession = Depends(get_async_session),
    user_id: int = Depends(get_current_user),
):
    result = await db.execute(select(Post).filter(Post.id == post_id))
    existing_post = result.scalars().first()
    if not existing_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )
    if existing_post.author_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this post",
        )
    if post.title is not None:
        existing_post.title = post.title
    if post.text is not None:
        existing_post.text = post.text
    existing_post.is_blocked = await asyncio.to_thread(
        is_text_toxic, f"{post.title} {post.text}"
    )
    db.add(existing_post)
    await db.commit()
    if existing_post.is_blocked:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Your post has been blocked because of toxic content.",
        )
    return existing_post


@post_router.delete("/{post_id}", response_model=dict)
async def delete_post(
    post_id: int,
    db: AsyncSession = Depends(get_async_session),
    user_id: int = Depends(get_current_user),
):
    result = await db.execute(select(Post).filter(Post.id == post_id))
    existing_post = result.scalars().first()
    if not existing_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )
    if existing_post.author_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this post",
        )

    await db.delete(existing_post)
    await db.commit()
    return {"msg": "Post successfully deleted"}
