from datetime import timedelta
from typing import Optional

from fastapi_users import schemas
from pydantic import Field


class UserRead(schemas.BaseUser[int]):
    auto_reply_enabled: bool = Field(default=False)
    auto_reply_delay: Optional[timedelta] = Field(default=None)


class UserCreate(schemas.BaseUserCreate):
    auto_reply_enabled: bool = Field(default=False)
    auto_reply_delay: Optional[timedelta] = Field(default=timedelta(seconds=10))


class UserUpdate(schemas.BaseUserUpdate):
    auto_reply_enabled: Optional[bool] = Field(default=None)
    auto_reply_delay: Optional[timedelta] = Field(default=None)
