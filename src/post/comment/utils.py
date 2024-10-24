from fastapi import HTTPException
from sqlalchemy import update, func
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Comment

from sqlalchemy import select


async def get_max_rgt(db: AsyncSession, post_id: int):
    max_rgt_for_post = await db.execute(
        select(func.max(Comment.rgt))
        .filter(Comment.post_id == post_id)
        .with_for_update()
    )
    max_rgt_for_post_value = max_rgt_for_post.scalar()

    if max_rgt_for_post_value is None:
        max_rgt_all_comments = await db.execute(
            select(func.max(Comment.rgt)).with_for_update()
        )
        max_rgt = max_rgt_all_comments.scalar() or 0
    else:
        max_rgt = max_rgt_for_post_value

    return max_rgt


async def comment_children_create(db: AsyncSession, post_id, comment_data, user):
    parent_result = await db.execute(
        select(Comment).filter(
            Comment.id == comment_data.parent_id, Comment.post_id == post_id
        )
    )
    parent_comment = parent_result.scalar_one_or_none()
    if parent_comment is None:
        raise HTTPException(
            status_code=400,
            detail=f"Comment with id №{comment_data.parent_id} not found.",
        )
    max_rgt_result = await db.execute(
        select(func.max(Comment.rgt)).filter(Comment.parent_id == parent_comment.id)
    )
    max_rgt = max_rgt_result.scalar_one_or_none()
    if max_rgt is not None:
        rgt_to_use = max_rgt
    else:
        rgt_to_use = parent_comment.rgt

    new_comment = Comment(
        content=comment_data.content,
        parent_id=comment_data.parent_id,
        post_id=post_id,
        user_id=user.id,
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
