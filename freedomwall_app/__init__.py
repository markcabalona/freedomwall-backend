import imp
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from freedomwall_app.routers import post,comment
from freedomwall_app.websockets import all_posts_websocket

from freedomwall_app import models,database

app = FastAPI()

models.Base.metadata.create_all(database.engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(post.router)
app.include_router(comment.router)
app.include_router(all_posts_websocket.router)