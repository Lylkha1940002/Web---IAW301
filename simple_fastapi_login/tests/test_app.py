from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_ping():
    r = client.get("/ping")
    assert r.status_code == 200
    assert r.text == "pong"

def test_login_form():
    r = client.get("/login-form")
    assert r.status_code == 200
    assert "Đăng nhập" in r.text

def test_protected_page():
    r = client.get("/me")
    assert r.status_code == 303
    assert "/login-form" in r.headers["location"]
