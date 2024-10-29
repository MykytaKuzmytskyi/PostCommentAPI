from asgiref.sync import async_to_sync
from celery import Celery, shared_task

from config import settings
from database.database import SessionLocal
from src.post.comment.utils import comment_children_create
from .generate_response import generate_response

celery = Celery(
    "src.services.celery_app",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_BACKEND_URL,
)

celery.conf.update(
    result_expires=3600,
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    broker_connection_retry_on_startup=True,
)


@shared_task
def reply_comment(post_id, parent_id, author_id, content, author_username):
    async_to_sync(reply_comment_async)(post_id, parent_id, author_id, content, author_username)


async def reply_comment_async(post_id, parent_id, author_id, content, author_username):
    async with SessionLocal() as db:
        content_response = generate_response(content, author_username)
        new_reply = await comment_children_create(
            db,
            post_id,
            parent_id,
            content_response,
            author_id,
            is_blocked=False,
        )
        db.add(new_reply)
        await db.commit()
        await db.refresh(new_reply)
