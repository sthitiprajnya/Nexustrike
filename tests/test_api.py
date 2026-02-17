import importlib.util

import pytest


pytestmark = pytest.mark.skipif(importlib.util.find_spec("fastapi") is None, reason="fastapi not installed in environment")


def test_start_and_report_flow():
    from fastapi.testclient import TestClient
    from backend.api.main import app

    client = TestClient(app)
    payload = {"message": "example.com", "authorization_token": "auth-token"}
    response = client.post("/api/v1/pentest/start", json=payload)
    assert response.status_code == 200

    thread_id = response.json()["thread_id"]
    report = client.get(f"/api/v1/pentest/{thread_id}/report")
    assert report.status_code == 200
    assert report.json()["thread_id"] == thread_id
