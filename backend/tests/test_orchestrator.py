from __future__ import annotations

from types import SimpleNamespace
from analysis.detector import AnalysisResult
from verification.orchestrator import VerificationAssistant


def fake_explainer_explain(request):
    return {"summary": "fake explanation", "used_llm": False}


class FakeAssistant(VerificationAssistant):
    def __init__(self, **kwargs):
def _analysis():
    return AnalysisResult(
        media_type="image",
        anomaly_score=0.4,
        face_detections=[],
        artifact_findings=[{"name": "noise", "score": 0.2, "detail": "low"}],
        metadata={},
        processing_notes=["note"],
    )
        anomaly_score=0.4,
        overall_score=45.0,
        face_detections=[],
        metadata={},
    )


def test_synthesize_returns_expected_keys():
    assistant = FakeAssistant(use_gemini=False)
    result = assistant.synthesize(_analysis(), "/tmp/fake.png", "image")
    payload = assistant.to_dict(result)

    assert "score" in payload
    assert "analysis" in payload
    assert "explanation" in payload
    assert "reverse_search" in payload
    assert payload["score"]["overall"] >= 0.0
    assert payload["score"]["overall"] <= 100.0


def test_source_score_scales_with_credibility():
    assistant = FakeAssistant(use_gemini=False)
    credibility = {"score": 80}
    provenance = {"available": True}
    reverse_search = {"enabled": True, "matches": [{"title": "x"}]}

    score = assistant._source_score(credibility, provenance, reverse_search)
    assert 80.0 <= score <= 100.0
