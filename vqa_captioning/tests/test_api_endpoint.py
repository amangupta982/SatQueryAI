"""
Tests for FastAPI VQA endpoint (POST /api/v1/vqa).
"""

import io
import base64
import pytest
from PIL import Image
from fastapi.testclient import TestClient

from frontend_backend.backend.main import app

client = TestClient(app)

def test_health_check_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["vqa_model"] == "SatQuery-VQA"

def test_vqa_endpoint_with_image_upload():
    # Create test image in-memory
    img = Image.new("RGB", (120, 120), color=(50, 150, 200))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)

    response = client.post(
        "/api/v1/vqa",
        data={"question": "Is water present?", "sensor": "Sentinel-2"},
        files={"image": ("test_patch.png", buf, "image/png")},
    )

    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert data["model"] == "SatQuery-VQA"
    assert data["task"] == "presence"

def test_vqa_endpoint_with_base64_image():
    img = Image.new("RGB", (60, 60), color=(10, 200, 50))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    b64_str = base64.b64encode(buf.getvalue()).decode("utf-8")

    response = client.post(
        "/api/v1/vqa",
        data={"question": "Is vegetation present?", "image_b64": b64_str},
    )

    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert data["model"] == "SatQuery-VQA"

def test_vqa_endpoint_missing_image_returns_400():
    response = client.post(
        "/api/v1/vqa",
        data={"question": "Where is the forest?"},
    )
    assert response.status_code == 400
    assert "An image must be provided" in response.json()["detail"]

def test_vqa_endpoint_empty_question_returns_422_or_400():
    img = Image.new("RGB", (60, 60), color=(10, 20, 30))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)

    response = client.post(
        "/api/v1/vqa",
        data={"question": "   "},
        files={"image": ("test.png", buf, "image/png")},
    )
    assert response.status_code == 400
