from typing import List
import json as json

from fastapi import APIRouter, Depends, status
from fastapi.encoders import jsonable_encoder

from sqlalchemy.orm import Session
from starlette.websockets import WebSocket, WebSocketDisconnect

from .. import crud, database, schemas
from .parameters import Params
from .provider import ConnectionType, provider

router = APIRouter()

get_db = database.get_db


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, db: Session = Depends(get_db)):
    await provider.connect(websocket,connection_type=ConnectionType.ALL_POSTS_CONNECTION)
    try:
        while True:
            await websocket.receive_text()
            posts = crud.get_all_posts(db, creator=None, title=None)
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

    except WebSocketDisconnect:
        await provider.remove(websocket,connection_type=ConnectionType.ALL_POSTS_CONNECTION)


@router.websocket("/ws/posts")
async def websocket_endpoint(websocket: WebSocket, db: Session = Depends(get_db)):
    await provider.connect(
        websocket=websocket, connection_type=ConnectionType.ALL_POSTS_CONNECTION
    )
    try:
        while True:
            await websocket.receive_text()
            posts = crud.get_all_posts(db, creator=None, title=None)
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

    except WebSocketDisconnect:
        provider.remove(websocket, connection_type=ConnectionType.ALL_POSTS_CONNECTION)


@router.websocket("/ws/postCreate")
async def create_post_websocket(websocket: WebSocket, db: Session = Depends(get_db)):
    await provider.connect(
        websocket=websocket, connection_type=ConnectionType.SPECIFIC_POST_CONNECTION
    )
    try:
        while True:
            request = await websocket.receive_text()
            # request_json = json.load(request)
            post = crud.create_post(db=db, post=schemas.PostCreate(data=request))
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

    except WebSocketDisconnect:
        provider.remove(
            websocket, connection_type=ConnectionType.SPECIFIC_POST_CONNECTION
        )


@router.post("/postCreate/", status_code=status.HTTP_201_CREATED)
async def create_post(request: schemas.PostCreate, db: Session = Depends(get_db)):
    response = crud.create_post(db=db, post=request)
    await provider.push(
        params=Params(id=response.id),
        db=db,
    )
    return {"detail": "Post Created"}


@router.put("/{id}", status_code=status.HTTP_202_ACCEPTED, response_model=schemas.Post)
async def like_or_dislike_post(
    id: int, action: crud.Action, db: Session = Depends(get_db)
):
    return crud.like_dislike_post(db, id, action)


@router.websocket("/ws/post/")
async def post_by_id_websocket(websocket: WebSocket, db: Session = Depends(get_db)):
    await provider.connect(websocket)
    try:
        while True:
            request = await websocket.receive_text()
            request_json = json.load(request)
            post = crud.get_post(db=db, post_id=request_json["id"])
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

    except WebSocketDisconnect:
        provider.remove(websocket)


@router.on_event("startup")
async def startup():
    # Prime the push notification generator
    await provider.generator.asend(None)
