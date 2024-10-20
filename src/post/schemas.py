from datetime import datetime

from pydantic import BaseModel


class PostBase(BaseModel):
    title: str
    content: str


class PostReadDetail(PostBase):
    id: int
    created_at: datetime
    user_id: int

    class Config:
        from_attributes = True


class PostCreate(PostBase):

    class Config:
        from_attributes = True


class PostCreateResponse(PostCreate):
    id: int


class PostUpdate(PostBase):
    pass
