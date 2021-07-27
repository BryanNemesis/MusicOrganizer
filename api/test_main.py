from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def test_collection_list():
    response = client.get("/collections")
    assert response.status_code == 200
    