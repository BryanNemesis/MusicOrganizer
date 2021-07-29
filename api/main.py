from os import environ

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from handlers import database, spotify


app = FastAPI()
# User ID will need to be obtained from session cookies or sth like that.
user_id = environ.get('SPOTIFY_USER_ID')


class Collection(BaseModel):
    user_id: str
    title: str


@app.get("/collections")
def collection_list():
    return database.get_collection_list(user_id)


@app.post("/collections")
def collection_create(collection: Collection):
    return database.create_collection(user_id, collection.dict())


@app.delete("/collections/{collection_title}")
def collection_delete(collection_title: str):
    return database.delete_collection(user_id, collection_title)


@app.get("/collections/{collection_title}")
def collection_detail(collection_title: str):
    response = database.get_collection_detail(user_id, collection_title)
    try:
        response['Item']
        return response
    except KeyError:
        return HTTPException(404, f'Collection with title {collection_title} not found.')


@app.post("/collections/{collection_title}")
def collection_add_album(collection_title: str, album_id: str):
    album = spotify.get_album(album_id)
    return database.add_album_to_collection(user_id, collection_title, album)


@app.delete("/collections/{collection_title}/{album_id}")
def collection_delete_album(collection_title: str, album_id: str):
    return database.delete_album_from_collection(user_id, collection_title, album_id)


@app.get("/albums/{query}")
def album_list(query: str):
    return spotify.get_album_list(query)
