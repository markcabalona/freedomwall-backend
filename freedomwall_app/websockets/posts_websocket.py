from typing import Optional


import asyncio

from fastapi import APIRouter, Depends, status
from fastapi.encoders import jsonable_encoder

from sqlalchemy.orm import Session
from starlette.websockets import WebSocket, WebSocketDisconnect

from .. import crud, database, schemas
from .parameters import Params
from .provider import Connection, provider

router = APIRouter(prefix="/post", tags=["Posts"])

get_db = database.get_db


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    creator: Optional[str] = None,
    title: Optional[str] = None,
    db: Session = Depends(get_db),
):
    connection = Connection(
        websocket=websocket, params=Params(creator=creator, title=title)
    )
    await provider.connect(connection=connection)
    try:
        while True:
            posts = crud.get_all_posts(db, creator=creator, title=title)
            postsJson = []
            for post in posts:
                db.refresh(post)
                postsJson.append(
                    {
                        "id": post.id,
                        "creator": post.creator,
                        "title": post.title,
                        "content": post.content,
                        "date_created": post.date_created,
                        "likes": post.likes,
                        "dislikes": post.dislikes,
                        "comments": [comment.__dict__ for comment in post.comments],
                    }
                )
            _json = jsonable_encoder(postsJson)
            await websocket.send_json(_json)
            await asyncio.sleep(30)

    except WebSocketDisconnect:
        provider.remove(connection=connection)


@router.websocket("/ws/post/{id}")
async def post_by_id_websocket(
    websocket: WebSocket, id: int, db: Session = Depends(get_db)
):
    connection = Connection(websocket=websocket, params=Params(id=id))
    await provider.connect(connection=connection)
    try:
        while True:
            post = crud.get_post(db=db, post_id=id)
            db.refresh(post)
            postJson = {
                "id": post.id,
                "creator": post.creator,
                "title": post.title,
                "content": post.content,
                "date_created": post.date_created,
                "likes": post.likes,
                "dislikes": post.dislikes,
                "comments": [comment.__dict__ for comment in post.comments],
            }
            _json = jsonable_encoder(postJson)
            await websocket.send_json(_json)
            await asyncio.sleep(30)

    except WebSocketDisconnect:
        provider.remove(connection=connection)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_post(request: schemas.PostCreate, db: Session = Depends(get_db)):
    response = crud.create_post(db=db, post=request)
    await provider.push(
        params=Params(id=response.id),
        db=db,
    )
    return response


@router.put("/{id}", status_code=status.HTTP_202_ACCEPTED, response_model=schemas.Post)
async def like_or_dislike_post(
    id: int, action: crud.Action, db: Session = Depends(get_db)
):
    response = crud.like_dislike_post(db=db, action=action, post_id=id)
    await provider.push(db=db, params=Params(id=id))
    return response


@router.post(
    "/{post_id}/comment",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.Comment,
)
async def create_comment(
    request: schemas.CommentCreate, post_id: int, db: Session = Depends(get_db)
):
    comment = crud.create_comment(db, request, post_id)
    await provider.push(db=db, params=Params(id=post_id))
    return comment


@router.on_event("startup")
async def startup():
    # Prime the push notification generator
    await provider.generator.asend(None)
