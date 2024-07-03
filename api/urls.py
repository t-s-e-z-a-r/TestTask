from fastapi import APIRouter

from .posts import posts_router
from .comments import comments_router

api_router = APIRouter()

api_router.include_router(posts_router, prefix="/posts", tags=["Posts"])
api_router.include_router(comments_router, prefix="/comments", tags=["Comments"])