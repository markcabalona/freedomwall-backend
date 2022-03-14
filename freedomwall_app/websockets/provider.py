from enum import Enum
from typing import Optional, List

# from fastapi import Depends
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder

from starlette.websockets import WebSocket
from .parameters import Params
from .. import crud


class ConnectionType(Enum):
    ALL_POSTS_CONNECTION = 1
    SPECIFIC_POST_CONNECTION = 2
    FILTERED_POST_CONNECTION = 3


class Provider:
    def __init__(self):
        self.all_post_connections: List[WebSocket] = []
        self.specific_post_connections: List[WebSocket] = []
        self.filtered_post_connections: List[WebSocket] = []
        self.generator = self.get_notification_generator()

    async def get_notification_generator(self):
        while True:
            notify_params = yield
            print(notify_params)
            await self._notify(db=notify_params[0], params=notify_params[1])

    async def push(self, db: Session, params: Optional[Params] = None):
        await self.generator.asend((db, params))

    async def connect(self, websocket: WebSocket, connection_type: ConnectionType):
        await websocket.accept()
        if connection_type is ConnectionType.ALL_POSTS_CONNECTION:
            self.all_post_connections.append(websocket)
        elif connection_type is ConnectionType.SPECIFIC_POST_CONNECTION:
            self.specific_post_connections.append(websocket)
        else:
            self.filtered_post_connections.append(websocket)

    def remove(self, websocket: WebSocket,connection_type:ConnectionType):
        if connection_type is ConnectionType.ALL_POSTS_CONNECTION:
            self.all_post_connections.remove()(websocket)
        elif connection_type is ConnectionType.SPECIFIC_POST_CONNECTION:
            self.specific_post_connections.remove()(websocket)
        else:
            self.filtered_post_connections.remove(websocket)

    async def _notify(self, db: Session, params: Params):
        await self._notify_all_posts(db=db)
        await self._notify_specific_posts(db=db, post_id=params.id)
        await self._notify_filtered_posts(db=db, params=params)

    async def _notify_all_posts(self, db: Session):
        response = crud.get_all_posts(db=db, creator=None, title=None)
        postsJson = []
        try:
            for post in response:
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
        finally:
            _json = jsonable_encoder(postsJson)
            print(type(_json))
            for connection in self.all_post_connections:
                await connection.send_json(_json)

    async def _notify_specific_posts(self, db: Session, post_id: int):
        if len(self.specific_post_connections) != 0:
            response = crud.get_post(db=db, post_id=post_id)
            db.refresh(response)
            _json = jsonable_encoder(response)
            for connection in self.specific_post_connections:
                await connection.send_json(_json)

    async def _notify_filtered_posts(self, db: Session, params: Params):
        if len(self.filtered_post_connections) != 0:
            response = crud.get_all_posts(
                db=db, creator=params.creator, title=params.title
            )
            db.refresh(response)
            _json = jsonable_encoder(response)
            for connection in self.filtered_post_connections:
                await connection.send_json(_json)


provider = Provider()
