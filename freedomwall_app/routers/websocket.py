import logging as log
from typing import Dict
from fastapi import APIRouter, WebSocket, Depends
import random

from fastapi.encoders import jsonable_encoder

from sqlalchemy.orm import Session

import asyncio

from .. import database, schemas, crud

get_db = database.get_db

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(ws: WebSocket, db: Session = Depends(get_db)):
    log.info(msg="Accepting client connection...")
    await ws.accept()
    while True:
        try:
            # get all posts
            posts = crud.get_all_posts(db, creator=None, title=None)
            postsJson = []
            # db.commit()
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
            json = jsonable_encoder(postsJson)
            await ws.send_json(json)
            await asyncio.sleep(0.2)
            # await asyncio.sleep(60 * 1)  # sleep for 5 mins

        except Exception as e:
            log.exception(msg=e)
            break
