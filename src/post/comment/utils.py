from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy import update, func
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Comment


async def get_parent_comment(db: AsyncSession, parent_id: int, post_id: int):
    """Get a parent's comment."""
    parent_result = await db.execute(
        select(Comment).filter(Comment.id == parent_id, Comment.post_id == post_id)
    )
    parent_comment = parent_result.scalar_one_or_none()
    if parent_comment is None:
        raise HTTPException(
            status_code=400,
            detail=f"Comment with id №{parent_id} not found.",
        )
    return parent_comment


async def get_max_rgt(db: AsyncSession, post_id: int):
    max_rgt_for_post = await db.execute(
        select(func.max(Comment.rgt))
        .filter(Comment.post_id == post_id)
    )
    max_rgt_for_post_value = max_rgt_for_post.scalar()

    if max_rgt_for_post_value is None:
        max_rgt_all_comments = await db.execute(
            select(func.max(Comment.rgt))
        )
        max_rgt = max_rgt_all_comments.scalar() or 0
    else:
        max_rgt = max_rgt_for_post_value

    return max_rgt


async def get_max_rgt_for_children(db: AsyncSession, parent_id: int):
    """We get the maximum rgt for child comments."""
    max_rgt_result = await db.execute(
        select(func.max(Comment.rgt)).filter(Comment.parent_id == parent_id)
    )
    return max_rgt_result.scalar_one_or_none()


async def shift_comment_tree(db: AsyncSession, max_rgt: int):
    """We move all comments with rgt > max_rgt to insert a new comment."""
    await db.execute(
        update(Comment)
        .where(Comment.lft > max_rgt)
        .values(lft=Comment.lft + 2, rgt=Comment.rgt + 2)
    )


async def comment_children_create(
    db: AsyncSession, post_id, parent_id, content, user_id, is_blocked
):
    """Creating a child comment."""
    parent_comment = await get_parent_comment(db, parent_id, post_id)

    max_rgt = await get_max_rgt_for_children(db, parent_comment.id)
    rgt_to_use = max_rgt if max_rgt is not None else parent_comment.rgt

    new_comment = Comment(
        post_id=post_id,
        parent_id=parent_id,
        content=content,
        user_id=user_id,
        is_blocked=is_blocked,
        lft=rgt_to_use,
        rgt=rgt_to_use + 1,
        level=parent_comment.level + 1,
    )

    await db.execute(
        update(Comment).where(Comment.lft > rgt_to_use).values(lft=Comment.lft + 2)
    )
    await db.execute(
        update(Comment).where(Comment.rgt >= rgt_to_use).values(rgt=Comment.rgt + 2)
    )

    return new_comment
