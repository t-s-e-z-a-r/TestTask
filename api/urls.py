from fastapi import APIRouter

from .posts import post_router
from .comments import comment_router
from .analytics import analytics_router

api_router = APIRouter()

api_router.include_router(post_router, prefix="/posts", tags=["Posts"])
api_router.include_router(comment_router, prefix="/comments", tags=["Comments"])
api_router.include_router(analytics_router, prefix="/analytics", tags=["Analytics"])
