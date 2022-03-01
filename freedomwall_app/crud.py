from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from . import models,schemas

from enum import Enum

class Action(str,Enum):
    like = "likes"
    dislike = "dislikes"

def get_all_posts(db:Session,creator:Optional[str],title:Optional[str]):
    if(creator and title):
            return db.query(models.Post).filter(models.Post.creator == creator).filter(models.Post.title == title).all()

    elif(creator or title):
        if(creator):        
            return db.query(models.Post).filter(models.Post.creator == creator).all()

        else:
            return db.query(models.Post).filter(models.Post.title == title).all()

    else:
        return db.query(models.Post).all()

def get_post(db:Session, post_id: int):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()

    if not post:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND,detail="Post not found")

    return post

def get_post_by_title(db:Session, title: str):
    return db.query(models.Post).filter(models.Post.title == title).all()

    
def get_post_by_creator(db:Session, creator: str):
    return db.query(models.Post).filter(models.Post.creator == creator).all()

def create_post(db:Session,post = schemas.PostCreate):
    new_post = models.Post(creator = post.creator,title = post.title,content = post.content)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

def delete_post(db:Session,post_id:int):
    post = db.query(models.Post).filter(models.Post.id == post_id)
    if not post.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id {post_id} is not found")
    
    post.delete(synchronize_session=False)
    db.commit()
    return {"detail":f"Post with id {post_id} has been deleted."}

def like_dislike_post(db:Session,post_id: int,action:str):
    post = db.query(models.Post).filter(models.Post.id == post_id)

    if not post.first():
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND,detail="Post not found")
    
    post.first().__setattr__(action, post.first().__getattribute__(action)+1)
    db.commit()

    return post.first()
    
def create_comment(db:Session,comment:schemas.CommentCreate,post_id:int):
    new_comment = models.Comment(content = comment.content)
    new_comment.__setattr__("post_id", post_id)
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    return new_comment

def get_all_comments(db:Session,post_id:int):
    return db.query(models.Comment).filter(models.Comment.post_id == post_id).all()

def get_comment(db:Session,id : int,post_id: int):
    comment = db.query(models.Comment).filter(models.Comment.id == id and models.Comment.post_id == post_id).first()

    if not comment:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND,detail="Comment not found")

    return comment

def delete_comment(db:Session,post_id:int,id:int):
    comment = db.query(models.Comment).filter(models.Comment.post_id == post_id and models.Comment.id == id)
    if not comment.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Comment with id {id} is not found")
    
    comment.delete(synchronize_session=False)
    db.commit()
    return {"detail":f"Comment with id {id} has been deleted."}

def like_dislike_comment(db:Session,id: int,post_id:int,action:str):
    comment = db.query(models.Comment).filter(models.Comment.id == id and models.Comment.post_id == post_id)

    if not comment.first():
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND,detail="Comment not found")
    
    comment.first().__setattr__(action, comment.first().__getattribute__(action)+1)
    db.commit()

    return comment.first()
 