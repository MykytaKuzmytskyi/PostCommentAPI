from asgiref.sync import async_to_sync
from celery import Celery, shared_task

from config import settings
from database.database import SessionLocal
from src.post.comment.utils import comment_children_create

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
def reply_comment(post_id, parent_id, user_id):
    async_to_sync(reply_comment_async)(post_id, parent_id, user_id)


async def reply_comment_async(post_id, parent_id, user_id):
    async with SessionLocal() as db:
        new_reply = await comment_children_create(
            db,
            post_id,
            parent_id,
            "RepLY Comment",
            user_id,
            is_blocked=False,
        )
        db.add(new_reply)
        await db.commit()
        await db.refresh(new_reply)
