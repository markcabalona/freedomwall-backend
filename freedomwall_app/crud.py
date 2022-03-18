from re import A
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from fastapi import HTTPException, status
from . import models, schemas

from enum import Enum


class Action(str, Enum):
    like = "likes++"
    un_like = "likes--"
    dislike = "dislikes++"
    un_dislike = "dislikes--"


def get_all_posts(db: Session, creator: Optional[str], title: Optional[str]):
    if creator and title:
        return (
            db.query(models.Post)
            .filter(models.Post.creator.like(f"%{creator}%"))
            .filter(models.Post.title.like(f"%{title}%"))
            .order_by(desc(models.Post.date_created))
            .all()
        )

    elif creator or title:
        if creator:
            return (
                db.query(models.Post)
                .filter(models.Post.creator.like(f"%{creator}%"))
                .order_by(desc(models.Post.date_created))
                .all()
            )

        else:
            return (
                db.query(models.Post)
                .filter(models.Post.title.like(f"%{title}%"))
                .order_by(desc(models.Post.date_created))
                .all()
            )

    else:
        return db.query(models.Post).order_by(desc(models.Post.date_created)).all()


def get_post(db: Session, post_id: int):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )

    return post


def create_post(db: Session, post=schemas.PostCreate):
    new_post = models.Post(creator=post.creator, title=post.title, content=post.content)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


def delete_post(db: Session, post_id: int):
    post = db.query(models.Post).filter(models.Post.id == post_id)
    if not post.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {post_id} is not found",
        )

    post.delete(synchronize_session=False)
    db.commit()
    return {"detail": f"Post with id {post_id} has been deleted."}


def like_dislike_post(db: Session, post_id: int, action: str):
    post = db.query(models.Post).filter(models.Post.id == post_id)

    if not post.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )

    if action is Action.like:
        post.first().__setattr__("likes", post.first().__getattribute__("likes") + 1)

    elif action is Action.un_like:
        count = post.first().__getattribute__("likes")
        if count > 0:
            post.first().__setattr__("likes", count - 1)

    elif action is Action.dislike:
        post.first().__setattr__(
            "dislikes", post.first().__getattribute__("dislikes") + 1)
    else:
        count = post.first().__getattribute__("dislikes")
        if count > 0:
            post.first().__setattr__("dislikes", count - 1)

    db.commit()
    db.refresh(post.first())

    return post.first()


def create_comment(db: Session, comment: schemas.CommentCreate, post_id: int):
    new_comment = models.Comment(content=comment.content)
    new_comment.__setattr__("post_id", post_id)
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)

    return new_comment

