
from datetime import datetime
from sqlalchemy import Column, Integer,String,ForeignKey,DateTime
from sqlalchemy.orm import relationship

from .database import Base

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    creator = Column(String)
    title = Column(String)
    content = Column(String, nullable=False)
    date_created = Column(DateTime, default=datetime.now)
    likes = Column(Integer,default=0)
    dislikes = Column(Integer,default=0)

    comments = relationship("Comment", back_populates="post")

class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    creator = Column(String, default="Anonymous")
    content = Column(String, nullable=False)
    date_created = Column(DateTime, default=datetime.now)
    likes = Column(Integer, default=0)
    dislikes = Column(Integer, default=0)
    post_id = Column(Integer,ForeignKey("posts.id"))

    post = relationship("Post", back_populates="comments")
