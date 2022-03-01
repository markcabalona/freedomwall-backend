from datetime import datetime
from venv import create
from pydantic import BaseModel
from typing import List, Optional


class CommentBase(BaseModel):
    creator: Optional[str] = "Anonymous"
    content: str = "A sample comment"
    
class CommentCreate(CommentBase):
    pass

class Comment(CommentBase):
    id: int
    post_id:int
    date_created: datetime
    likes: int
    dislikes: int

    class Config:
        orm_mode = True

class PostBase(BaseModel):
    creator: Optional[str] = "Anonymous"
    title: Optional[str] = "Untitled"
    content: str = "A sample post"

class PostCreate(PostBase):
    pass    

class Post(PostBase):
    creator: str
    title: str
    content: str
    id: int
    date_created: datetime
    comments: List[Comment] = []
    likes: int
    dislikes: int

    class Config:
        orm_mode = True

