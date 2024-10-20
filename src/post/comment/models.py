from sqlalchemy import Integer, Column, Text, func, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship

from database.database import Base


class Comment(Base):
    __tablename__ = 'comments'

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey('posts.id'), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    user_id = Column(Integer, ForeignKey("user.id"))

    is_blocked = Column(Boolean, default=False)
    parent_id = Column(Integer, ForeignKey('comments.id'), nullable=True)
    lft = Column(Integer, nullable=False)
    rgt = Column(Integer, nullable=False)
    level = Column(Integer, nullable=False, default=0)


    parent = relationship('Comment', remote_side=[id], backref="children")

    user = relationship("User", back_populates="comments")
    post = relationship("Post", back_populates="comments")