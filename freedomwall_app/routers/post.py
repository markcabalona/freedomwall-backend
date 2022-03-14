from typing import List, Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from .. import database,schemas,crud

router = APIRouter(
    prefix="/post",
    tags=['Posts']
)

get_db = database.get_db

@router.get('/',response_model=List[schemas.Post])
def get_all_posts(creator:Optional[str] = None,title:Optional[str] = None, db:Session = Depends(get_db)):
    return crud.get_all_posts(db,creator=creator,title=title)

@router.post('/',status_code=status.HTTP_201_CREATED,response_model=schemas.Post)
def create_post(request: schemas.PostCreate,db: Session =Depends(get_db)):
    return crud.create_post(db = db, post = request)

@router.get('/{id}',response_model=schemas.Post)
def get_post_by_id(id:int, db:Session =Depends(get_db)):
    return crud.get_post(db, id)

@router.delete('/{id}',status_code=status.HTTP_200_OK)
def delete_post(id:int, db:Session=Depends(get_db)):
    return crud.delete_post(db,id)

@router.put('/{id}',status_code=status.HTTP_202_ACCEPTED,response_model=schemas.Post)
def like_or_dislike_post(id:int,action:crud.Action, db:Session =Depends(get_db)):
    return crud.like_dislike_post(db,id,action)