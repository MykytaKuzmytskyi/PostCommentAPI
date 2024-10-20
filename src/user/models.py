from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable
from sqlalchemy import Integer, Column, Boolean, Interval
from sqlalchemy.orm import relationship

from database.database import Base


class User(SQLAlchemyBaseUserTable[int], Base):
    id = Column(Integer, primary_key=True, index=True)

    auto_reply_enabled = Column(Boolean, default=False)
    auto_reply_delay = Column(Interval, nullable=True)

    posts = relationship("Post", back_populates="user")
    comments = relationship("Comment", back_populates="user")
