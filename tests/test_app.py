import os
import json
from fastapi.testclient import TestClient
import importlib

# Ensure env is clean (no real key required for tests)
os.environ.pop("GROQ_API_KEY", None)

backend = importlib.import_module("backend")
client = TestClient(backend.app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"


def test_home_serves_index_or_404():
    r = client.get("/")
    assert r.status_code in (200, 404)


def test_chat_demo_mode_without_key():
    payload = {"message": "What is crop rotation?"}
    r = client.post("/chat", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert "reply" in data
    # Should get a meaningful response (either from search tools or demo mode)
    assert len(data["reply"]) > 50  # Ensure we get a substantial response
    assert "crop rotation" in data["reply"].lower()  # Should contain the topic


def test_greeting_path():
    payload = {"message": "hello"}
    r = client.post("/chat", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert "reply" in data
    # Expect formatted HTML with bold tag from format_response
    assert "<strong" in data["reply"]


def test_cors_preflight_like():
    # Simulate a CORS-like request by setting Origin; Starlette handles OPTIONS internally.
    r = client.options("/chat", headers={
        "Origin": "http://example.com",
        "Access-Control-Request-Method": "POST",
    })
    # Starlette returns 200 for allowed methods or 405 if route doesn't accept OPTIONS directly; middleware should handle it.
    assert r.status_code in (200, 204)
