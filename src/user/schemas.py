from datetime import timedelta
from fastapi_users import schemas
from pydantic import Field


class UserRead(schemas.BaseUser[int]):
    auto_reply_enabled: bool = Field(default=False)
    auto_reply_delay: timedelta = Field(default=None)


class UserCreate(schemas.BaseUserCreate):
    auto_reply_enabled: bool = Field(default=False)
    auto_reply_delay: timedelta = Field(default=None)


class UserUpdate(schemas.BaseUserUpdate):
    auto_reply_enabled: bool = Field(default=None)
    auto_reply_delay: timedelta = Field(default=None)
