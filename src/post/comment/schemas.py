from datetime import datetime

from pydantic import BaseModel


class CommentBase(BaseModel):
    content: str


class CommentsRead(CommentBase):
    id: int
    post_id: int
    created_at: datetime
    user_id: int

    class Config:
        from_attributes = True


class CommentTree(BaseModel):
    id: int
    created_at: datetime
    user_id: int
    content: str
    lft: int
    rgt: int
    children: list["CommentTree"] = []

    class Config:
        from_attributes = True


class CommentCreate(CommentBase):
    parent_id: int | None = None

    class Config:
        from_attributes = True
