from __future__ import annotations

import io
import os
import tempfile

import numpy as np
import pytest
from PIL import Image

from analysis.detector import analyze, AnalysisResult


def _write_temp_image(suffix: str = ".png") -> str:
    image = Image.fromarray(np.random.randint(0, 255, (64, 64, 3), dtype=np.uint8))
    fd, path = tempfile.mkstemp(suffix=suffix)
    os.close(fd)
    image.save(path)
    return path


@pytest.fixture()
def image_path():
    path = _write_temp_image(".png")
    yield path
    if os.path.exists(path):
        os.remove(path)
def test_analyze_image_returns_analysis_result(image_path):
    result = analyze(image_path, "image")

    assert isinstance(result, AnalysisResult)
    assert result.media_type == "image"
    assert isinstance(result.artifact_findings, list)
    assert isinstance(result.processing_notes, list)
    assert isinstance(result.anomaly_score, float)
    assert 0.0 <= result.anomaly_score <= 1.0
    assert isinstance(result.face_detections, list)
    assert isinstance(result.metadata, dict)


def test_analyze_rejects_unsupported_media_type(image_path):
    with pytest.raises(ValueError):
        analyze(image_path, "document")


def test_analyze_common_image_extensions(image_path):
    base = image_path
    for ext in (".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff"):
        path = base + ext
        Image.fromarray(np.random.randint(0, 255, (32, 32, 3), dtype=np.uint8)).save(path)
        try:
            result = analyze(path, "image")
            assert isinstance(result, AnalysisResult)
        finally:
            if os.path.exists(path):
                os.remove(path)
