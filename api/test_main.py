from os import environ

from pytest import fixture
from fastapi.testclient import TestClient
import boto3

from main import app
from handlers import database, spotify


client = TestClient(app)
user_id = environ.get('SPOTIFY_USER_ID')


@fixture()
def db_table():
    db = boto3.resource('dynamodb', endpoint_url="http://db-local:8000", region_name="eu-west-1")
    table = db.Table(name='collections')
    table.put_item(Item={'user_id': user_id, 'title': 'test', 'albums': []})
    yield table
    table.delete_item(Key={'user_id': user_id, 'title': 'test'})
    table.delete_item(Key={'user_id': user_id, 'title': 'test1'})


def test_collection_list(db_table):
    item = {'user_id': user_id, 'title': 'test', 'albums': []}
    response = client.get("/collections")
    assert response.status_code == 200
    assert item in response.json()['Items']


def test_collection_create(db_table):
    item = {'user_id': user_id, 'title': 'test1', 'albums': []}
    response = client.post("/collections", json=item)
    assert response.status_code == 200
    assert 'Item' in db_table.get_item(Key={'user_id': user_id, 'title': 'test1'}).keys()


def test_collection_delete(db_table):
    response = client.delete("/collections/test")
    assert response.status_code == 200
    assert 'Item' not in db_table.get_item(Key={'user_id': user_id, 'title': 'test'}).keys()


def test_collection_detail(db_table):
    item = {'user_id': user_id, 'title': 'test', 'albums': []}
    response = client.get("/collections/test")
    assert response.status_code == 200
    assert response.json()['Item'] == item


def test_collection_detail_404(db_table):
    response = client.get("/collections/test2")
    assert response.status_code == 200
    assert response.json()['status_code'] == 404


def test_collection_add_album(db_table):
    album_id = '3y3sJMXTBarPgGt37GDSVg'
    payload = {'album_id': album_id}
    response = client.post("/collections/test", params=payload)
    assert response.status_code == 200
    assert response.json()['Attributes']['albums'][0]['id'] == album_id


def test_collection_delete_album(db_table):
    album_id = '3y3sJMXTBarPgGt37GDSVg'
    album = spotify.get_album(album_id)
    database.add_album_to_collection(user_id, 'test', album)

    response = client.delete(f"/collections/test/{album_id}")
    assert response.status_code == 200
    assert db_table.get_item(Key={'user_id': user_id, 'title': 'test'})['Item']['albums'] == []
