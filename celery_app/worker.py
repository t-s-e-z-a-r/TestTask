import asyncio

from database.models import Comment
from database.config import async_session_maker

from celery_app.services import generate_auto_response

from celery import Celery
from datetime import datetime

celery_app = Celery(
    "worker",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/0",
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    broker_connection_retry_on_startup=True,
)


@celery_app.task(name="Auto-response")
def create_auto_response_comment(comment_id: int):
    asyncio.run(_create_auto_response_comment(comment_id))


async def _create_auto_response_comment(comment_id: int):
    async with async_session_maker() as session:
        print("Started")
        original_comment = await session.get(Comment, comment_id)
        if not original_comment:
            return

        response_text = generate_auto_response(original_comment.text)
        print(f"Response: {response_text}")
        new_comment = Comment(
            text=response_text,
            post_id=original_comment.post_id,
            author_id=original_comment.author_id,
            parent_id=original_comment.id,
            created_at=datetime.utcnow(),
        )

        session.add(new_comment)
        await session.commit()
