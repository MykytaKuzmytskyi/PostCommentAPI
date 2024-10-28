import asyncio

from fastapi import HTTPException
from sqlalchemy import insert, select, delete, update, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.post import models, schemas
from src.post.comment.models import Comment
from src.post.comment.schemas import CommentCreate, CommentTree
from src.post.comment.utils import (
    comment_children_create,
    get_max_rgt,
    shift_comment_tree,
)
from src.post.models import Post
from src.services.celery_app import reply_comment
from src.services.text_toxicity_analysis import analyze_text_toxicity
from src.user.models import User


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
    title_toxicity_score = await analyze_text_toxicity(post_data.title)
    content_toxicity_score = await analyze_text_toxicity(post_data.content)
    is_blocked = any([title_toxicity_score > 0.5, content_toxicity_score > 0.5])

    query = insert(models.Post).values(
        title=post_data.title,
        content=post_data.content,
        user_id=user.id,
        is_blocked=is_blocked,
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


async def get_comments_by_post(post_id: int, db: AsyncSession):
    await get_post_by_id(db, post_id)
    query = select(Comment).where(Comment.post_id == post_id)
    result = await db.execute(query)
    return result.scalars().all()


async def get_comment_by_comment_id(db: AsyncSession, comment_id: int):
    comment = await db.get(Comment, comment_id)
    if not comment:
        raise HTTPException(
            status_code=404, detail=f"Comment with id {comment_id} not found."
        )
    return comment


async def get_children_comments(db: AsyncSession, parent_id: int) -> list[Comment]:
    children_query = select(Comment).where(
        Comment.parent_id == parent_id
    )
    children_result = await db.execute(children_query)
    return children_result.scalars().all()


async def build_comment_tree(db: AsyncSession, comment: Comment) -> CommentTree:
    comment_tree = CommentTree(
        id=comment.id,
        content=comment.content,
        created_at=comment.created_at,
        user_id=comment.user_id,
        lft=comment.lft,
        rgt=comment.rgt,
    )
    children = await get_children_comments(db, comment.id)
    comment_tree.children = [await build_comment_tree(db, child) for child in children]
    return comment_tree


async def get_comments_tree(db: AsyncSession, post_id: int) -> list[CommentTree]:
    root_comments_query = select(Comment).where(
        Comment.post_id == post_id, Comment.parent_id.is_(None)
    )
    result = await db.execute(root_comments_query)
    root_comments = result.scalars().all()

    return await asyncio.gather(
        *(build_comment_tree(db, comment) for comment in root_comments)
    )


async def create_comment(
        db: AsyncSession, post_id: int, comment_data: CommentCreate, user
):
    await get_post_by_id(db, post_id)

    toxicity_score = await analyze_text_toxicity(comment_data.content)
    is_blocked = toxicity_score > 0.5

    result = await db.execute(select(func.count(Comment.id)))
    comments_count = result.scalar()
    if comments_count == 0:
        new_comment = Comment(
            post_id=post_id,
            parent_id=comment_data.parent_id,
            content=comment_data.content,
            user_id=user.id,
            is_blocked=is_blocked,
            lft=1,
            rgt=2,
            level=0,
        )
    else:
        if comment_data.parent_id is not None:
            new_comment = await comment_children_create(
                db,
                post_id,
                comment_data.parent_id,
                comment_data.content,
                user.id,
                is_blocked
            )
        else:
            max_rgt = await get_max_rgt(db, post_id)
            await shift_comment_tree(db, max_rgt)
            new_comment = Comment(
                post_id=post_id,
                parent_id=comment_data.parent_id,
                content=comment_data.content,
                user_id=user.id,
                is_blocked=is_blocked,
                lft=max_rgt + 1,
                rgt=max_rgt + 2,
                level=0,
            )

    db.add(new_comment)
    await db.commit()
    await db.refresh(new_comment)

    user_db = await db.execute(
        select(User).join(Post).where(Post.id == post_id)
    )
    user = user_db.scalar_one_or_none()
    if user.auto_reply_enabled:
        reply_comment.apply_async(
            args=[post_id, new_comment.id, user.id],
            countdown=user.auto_reply_delay.total_seconds()
        )

    return new_comment


async def delete_comment(db: AsyncSession, comment_id: int):
    comment = await get_comment_by_comment_id(db, comment_id)

    min_lft = comment.lft
    max_rgt = comment.rgt
    width = max_rgt - min_lft + 1

    await db.execute(
        delete(Comment).where(Comment.lft >= min_lft, Comment.rgt <= max_rgt)
    )
    await db.execute(
        update(Comment).where(Comment.lft > max_rgt).values(lft=Comment.lft - width)
    )
    await db.execute(
        update(Comment).where(Comment.rgt > max_rgt).values(rgt=Comment.rgt - width)
    )
    await db.commit()

    return
