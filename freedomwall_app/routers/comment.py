from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from .. import database,schemas,crud

router = APIRouter(
    prefix="/post",
    tags=['Comments']
)

get_db = database.get_db

@router.get('/{post_id}/comment',response_model=List[schemas.Comment])
def all_comments(post_id:int,db:Session = Depends(get_db)):
    return crud.get_all_comments(db,post_id)
    
@router.post('/{post_id}/comment',status_code=status.HTTP_201_CREATED,response_model=schemas.Comment)
def create_comment(request: schemas.CommentCreate,post_id:int,db: Session =Depends(get_db)):
    return crud.create_comment(db, request,post_id)

@router.get('/{post_id}/comment/{id}',response_model=schemas.Post)
def get_comment(id:int,post_id:int, db:Session =Depends(get_db)):
    return crud.get_comment(db, id = id,post_id=post_id)

@router.delete('/{post_id}/comment/{id}',status_code=status.HTTP_200_OK)
def delete_comment(id:int,post_id:int, db:Session=Depends(get_db)):
    return crud.delete_comment(db,id=id,post_id=post_id)

@router.put('/{post_id}/comment/{id}/{action}',status_code=status.HTTP_202_ACCEPTED,response_model=schemas.Post)
def like_or_dislike_comment(id:int,post_id:int,action:crud.Action, db:Session =Depends(get_db)):
    return crud.like_dislike_comment(db,id=id,action=action,post_id=post_id)