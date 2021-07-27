from os import environ

from fastapi import FastAPI
from pydantic import BaseModel

from handlers import database, spotify


app = FastAPI()
# User ID will need to be obtained from session cookies or sth like that.
user_id = environ.get('SPOTIFY_USER_ID')


class Collection(BaseModel):
    user_id: str
    title: str
    albums: list


@app.get("/collections")
def list():
    return database.get_collection_list(user_id)


@app.get("/collections/{collection_title}")
def detail(collection_title: str):
    return database.get_collection_detail(user_id, collection_title)


@app.post("/collections")
def create(collection: Collection):
    return database.create_collection(user_id, collection.dict())


@app.get("/albums/{query}")
def album_list(query: str):
    return spotify.get_album_list(query)


@app.post("/collections/{collection_title}")
def add_album_to_collection(collection_title: str, album_id: str):
    album = spotify.get_album(album_id)
    return database.add_album_to_collection(user_id, collection_title, album)