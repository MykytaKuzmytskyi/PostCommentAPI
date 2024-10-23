from fastapi import HTTPException
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.post import models, schemas


async def get_posts(db: AsyncSession):
    query = select(models.Post)
    result = await db.execute(query)
    return result.scalars().all()


async def get_post_by_id(db: AsyncSession, post_id: int):
    query = (
        select(models.Post)
        .options(selectinload(models.Post.comments))
        .where(models.Post.id == post_id)
    )
    result = await db.execute(query)
    post = result.unique().scalar_one_or_none()
    if not post:
        raise HTTPException(
            status_code=404, detail=f"The post with id {post_id} does not exist"
        )
    return post


async def post_create(db: AsyncSession, post_data: schemas.PostCreate, user):
    query = insert(models.Post).values(
        title=post_data.title,
        content=post_data.content,
        user_id=user.id,
    )

    result = await db.execute(query.returning(models.Post.id))
    new_post_id = result.scalar()
    await db.commit()

    return {**post_data.model_dump(), "id": new_post_id}


async def post_update(db: AsyncSession, post_data: schemas.PostUpdate, post_id: int):
    db_post = await get_post_by_id(db, post_id)
    for attr, value in post_data.dict().items():
        setattr(db_post, attr, value)

    await db.commit()
    await db.refresh(db_post)
    return db_post


async def post_delete(db: AsyncSession, post_id: int):
    db_post = await get_post_by_id(db, post_id)
    await db.delete(db_post)
    await db.commit()
    return HTTPException(
        status_code=204, detail=f"Post with id №{post_id} has been deleted."
    )
