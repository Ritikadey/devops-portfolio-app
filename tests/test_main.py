import os
import sys

# Allow running pytest from the repo root without packaging the app.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "app"))

import pytest
from main import app as flask_app


@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as client:
        yield client


def test_index_returns_200(client):
    response = client.get("/")
    assert response.status_code == 200


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    body = response.get_json()
    assert body["status"] == "healthy"
    assert "timestamp" in body


def test_info_endpoint(client):
    response = client.get("/api/info")
    assert response.status_code == 200
    body = response.get_json()
    assert "version" in body
    assert "environment" in body
