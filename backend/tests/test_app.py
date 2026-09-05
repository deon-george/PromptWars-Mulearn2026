from __future__ import annotations

import io
import os
import sys
import types
import pytest
from PIL import Image
import numpy as np

# Ensure backend imports work when tests run from project root.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app import app


def _create_image_bytes(suffix="png"):
    image = Image.fromarray(np.random.randint(0, 255, (64, 64, 3), dtype=np.uint8))
    buffer = io.BytesIO()
    image.save(buffer, format=suffix.upper())
    buffer.seek(0)
    return buffer.read(), suffix.lower()


@pytest.fixture()
def client(tmp_path, monkeypatch):
    uploads = tmp_path / "uploads"
    analysis = tmp_path / "static" / "analysis"
    uploads.mkdir()
    analysis.mkdir(parents=True)

    monkeypatch.setattr("app.UPLOAD_DIR", str(uploads))
    monkeypatch.setattr("app.ANALYSIS_DIR", str(analysis))
    monkeypatch.setenv("USE_GEMINI", "false")

    with app.test_client() as client:
        yield client


def test_health_route(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.get_json() == {"status": "ok"}


def test_analyze_requires_file(client):
    res = client.post("/api/analyze", data={})
    assert res.status_code == 400
    assert "error" in res.get_json()


def test_analyze_accepts_image(client, monkeypatch):
    data, suffix = _create_image_bytes("png")

    class FakeUpload:
        filename = f"test.{suffix}"
        def save(self, path):
            with open(path, "wb") as f:
                f.write(data)

    # Patch analysis and verification so endpoint runs fast and deterministically.
    fake_analysis = type("A", (), {
        "media_type": "image",
        "artifact_findings": [],
        "processing_notes": [],
        "anomaly_score": 0.5,
        "overall_score": 50.0,
        "face_detections": [],
        "metadata": {},
        "asdict": lambda self: {
            "media_type": self.media_type,
            "artifact_findings": self.artifact_findings,
            "processing_notes": self.processing_notes,
            "anomaly_score": self.anomaly_score,
            "overall_score": self.overall_score,
            "face_detections": self.face_detections,
            "metadata": self.metadata,
        },
    })()

    def fake_analyze(path, media_type):
        return fake_analysis

    monkeypatch.setattr("app.analyze", fake_analyze)

    assistant_instance = type("B", (), {
        "synthesize": lambda self, analysis, file_path, media_type: type("Payload", (), {
            "analysis": fake_analysis,
            "explanation": {"summary": "ok", "used_llm": False},
            "provenance": {},
            "metadata": {},
            "reverse_search": {"enabled": True},
            "credibility": {"score": 60},
            "ocr": {"enabled": False},
            "factcheck": {"contexts": []},
            "score": type("Score", (), {"overall": 60, "detection": 50, "source": 60, "explanation_confidence": 55})(),
        })(),
        "to_dict": lambda self, payload: {
            "score": {
                "overall": 60.0,
                "detection": 50.0,
                "source": 60.0,
                "explanation_confidence": 55.0,
            },
            "analysis": fake_analysis.asdict(),
            "explanation": {"summary": "ok", "used_llm": False},
            "provenance": {},
            "metadata": {},
            "reverse_search": {"enabled": True},
            "credibility": {"score": 60},
            "ocr": {"enabled": False},
            "factcheck": {"contexts": []},
        },
    })()

    monkeypatch.setattr("app.VerificationAssistant", lambda **kwargs: assistant_instance)

    data, _ = _create_image_bytes("png")
    res = client.post(
        "/api/analyze",
        data={"file": (io.BytesIO(data), "test.png")},
        content_type="multipart/form-data",
    )
    assert res.status_code == 200
    body = res.get_json()
    assert body["media_type"] == "image"
    assert "score" in body
    assert "analysis" in body
