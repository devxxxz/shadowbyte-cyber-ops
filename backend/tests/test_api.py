from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine

def setup_function():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

def test_health():
    with TestClient(app) as client:
        assert client.get("/health").json()["status"] == "ok"

def test_authorization_required():
    with TestClient(app) as client:
        r = client.post("/api/assets", json={
            "hostname": "not-authorized.example",
            "display_name": "Test asset",
            "authorized": False,
            "authorization_note": ""
        })
        assert r.status_code == 201
        asset_id = r.json()["id"]
        blocked = client.post(f"/api/assets/{asset_id}/assessments")
        assert blocked.status_code == 403

def test_authorized_asset_requires_note():
    with TestClient(app) as client:
        r = client.post("/api/assets", json={
            "hostname": "authorized.example",
            "authorized": True,
            "authorization_note": ""
        })
        assert r.status_code == 422

def test_invalid_hostname_rejected():
    with TestClient(app) as client:
        r = client.post("/api/assets", json={
            "hostname": "https://example.com/path",
            "authorized": True,
            "authorization_note": "Written permission"
        })
        assert r.status_code == 422
