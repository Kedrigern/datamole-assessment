from fastapi.testclient import TestClient
from sqlmodel import Session
from .test_database import prepare_data


def test_bad_url(client: TestClient):
    response = client.get("/abc")
    assert response.status_code == 404


def test_root(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "Hello" in data["info"]
    assert len(data["example_paths"]) == 5


def test_empty_db(client: TestClient):
    """
    Mock DB is empty
    """
    response = client.get("/stats/abc/abc")
    assert response.status_code == 404


def test_mock_data(client: TestClient, session: Session):
    prepare_data(session)
    response = client.get("/stats/org/repo1/PushEvent")
    assert response.status_code == 200
    data = response.json()
    assert data["repo"] == "org/repo1"
    assert data["type"] == "PushEvent"
    assert data["avg_time_diff"] == 3600
    assert data["avg_time_diff_unit"] == "seconds"
    assert data["avg_time_diff_str"] == "1:00:00"
    assert data["events_count"] == 7
