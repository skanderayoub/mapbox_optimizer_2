from fastapi.testclient import TestClient
from models.user import User
from repositories.users_repository import save_user


def test_create_user_endpoint(app_with_fake_db):
    client = TestClient(app_with_fake_db)
    resp = client.post("/users", json={})
    assert resp.status_code == 200
    data = resp.json()
    assert "id" in data


def test_get_user_endpoint(app_with_fake_db, patch_repositories_db):
    u = User(save_object=False)
    save_user(u)

    client = TestClient(app_with_fake_db)
    resp = client.get(f"/users/{u.id}")
    assert resp.status_code == 200
    fetched = resp.json()
    assert fetched["id"] == u.id


def test_update_user_endpoint(app_with_fake_db, patch_repositories_db):
    u = User(save_object=False)
    save_user(u)

    client = TestClient(app_with_fake_db)
    resp = client.patch(f"/users/{u.id}", json={"firstName": "Jane"})
    assert resp.status_code == 200
    updated = resp.json()
    assert updated["firstName"] == "Jane"


