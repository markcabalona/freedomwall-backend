from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from freedomwall_app.routers import post,comment,websocket

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
app.include_router(websocket.router)