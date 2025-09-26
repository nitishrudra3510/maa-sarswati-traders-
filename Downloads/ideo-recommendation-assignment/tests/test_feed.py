from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_missing_username():
    resp = client.get("/feed")
    assert resp.status_code == 422


def test_cold_start_empty_ok():
    resp = client.get("/feed", params={"username": "testuser"})
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_pagination_params_ok():
    resp = client.get("/feed", params={"username": "testuser", "limit": 5, "offset": 0})
    assert resp.status_code == 200


def test_category_param_ok():
    resp = client.get("/feed", params={"username": "testuser", "project_code": "fitness"})
    assert resp.status_code == 200


