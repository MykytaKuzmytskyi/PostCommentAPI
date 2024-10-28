from sqlalchemy import Integer, Column, Text, func, ForeignKey, DateTime, String, Boolean
from sqlalchemy.orm import relationship

from database.database import Base


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    user_id = Column(Integer, ForeignKey("user.id"))
    is_blocked = Column(Boolean, default=False)

    user = relationship("User", back_populates="posts")
    comments = relationship(
        "Comment", cascade="all, delete-orphan", back_populates="post"
    )
