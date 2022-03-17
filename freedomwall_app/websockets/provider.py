from typing import Optional, List

# from fastapi import Depends
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder

from starlette.websockets import WebSocket
import websockets
from .parameters import Params
from .. import crud


class Connection:
    def __init__(self, websocket: WebSocket, params: Optional[Params] = None):
        self.websocket = websocket
        self.params = params


class Provider:
    def __init__(self):
        self.connections: List[Connection] = []
        self.generator = self.get_notification_generator()

    def __del__(self):
        for connection in self.connections:
            self.remove(
                connection=connection,
            )

    async def get_notification_generator(self):
        while True:
            notify_params = yield
            await self._notify(db=notify_params)

    async def push(self, db: Session):
        self.generator.asend(db)

    async def connect(self, connection: Connection):
        await connection.websocket.accept()
        self.connections.append(connection)

    def remove(self, connection: Connection):
        connection.websocket.close()
        self.connections.remove(connection)

    async def _notify(self, db: Session):
        for connection in self.connections:
            if connection.params == None:
                response = crud.get_all_posts(db=db, creator=None, title=None)
            elif connection.params.id == None:
                response = crud.get_post(db=db, post_id=connection.params.id)
            else:
                response = crud.get_all_posts(
                    db=db,
                    creator=connection.params.creator,
                    title=connection.params.title,
                )
            if response is List:
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
                                "comments": [
                                    comment.__dict__ for comment in post.comments
                                ],
                            }
                        )
                finally:
                    _json = jsonable_encoder(postsJson)
                    await connection.websocket.send_json(_json)

            else:
                try:
                    db.refresh(response)
                    postJson = {
                        "id": response.id,
                        "creator": response.creator,
                        "title": response.title,
                        "content": response.content,
                        "date_created": response.date_created,
                        "likes": response.likes,
                        "dislikes": response.dislikes,
                        "comments": [comment.__dict__ for comment in response.comments],
                    }
                finally:
                    _json = jsonable_encoder(postJson)
                    await connection.websocket.send_json(_json)


provider = Provider()
