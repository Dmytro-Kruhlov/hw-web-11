from fastapi.testclient import TestClient

from main import app
from src.schemas import ResponseContact

client = TestClient(app)


def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "REST APP v1.2"}


def test_get_contact():
    response = client.get("/contacts")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    for contact in data:
        assert ResponseContact(**contact)

