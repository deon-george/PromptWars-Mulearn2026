from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

from analysis.detector import AnalysisResult
from explanation.explainer import ExplanationLayer, ExplanationRequest
from verification.exif import inspect_metadata
from verification.reverse_search import reverse_search_summary
from verification.credibility import assess_credibility
from verification.ocr import ocr_summary
from verification.factcheck import build_factcheck_context


@dataclass
class MediaSyntheticScore:
    overall: float
    detection: float
    source: float
    explanation_confidence: float


@dataclass
class VerificationPayload:
    analysis: Dict[str, Any]
    explanation: Dict[str, Any]
    provenance: Dict[str, Any]
    metadata: Dict[str, Any]
    reverse_search: Dict[str, Any]
    credibility: Dict[str, Any]
    ocr: Dict[str, Any]
    factcheck: Dict[str, Any]
    score: MediaSyntheticScore


class VerificationAssistant:
    def __init__(self, use_gemini: bool = False, gemini_model: Optional[str] = None):
        self.explainer = ExplanationLayer(use_gemini=use_gemini, gemini_model=gemini_model)

    def _source_score(self, credibility: Dict[str, Any], provenance: Dict[str, Any], reverse_search: Dict[str, Any]) -> float:
        base = float(credibility.get('score') or 50)
        prov_bonus = 15 if provenance.get('available') else 0
        rev_bonus = 10 if reverse_search.get('enabled') and reverse_search.get('matches') else 0
        return float(max(0.0, min(100.0, base + prov_bonus + rev_bonus)))

    def synthesize(self, analysis: AnalysisResult, file_path: str, media_type: str, source_url: Optional[str] = None) -> VerificationPayload:
        top_signals = [(f['name'], float(f['score'])) for f in analysis.artifact_findings]
        if not top_signals:
            top_signals = [('no_signals', 0.5)]

        explanation_req = ExplanationRequest(
            media_type=media_type,
            score=analysis.anomaly_score * 100.0,
            top_signals=top_signals,
            artifact_findings=analysis.artifact_findings,
            face_detections=analysis.face_detections,
            metadata=analysis.metadata,
        )
        explanation = self.explainer.explain(explanation_req)

        provenance = {}
        metadata = inspect_metadata(file_path, media_type=media_type)
        reverse_search = reverse_search_summary(file_path) if media_type == 'image' else {'enabled': False, 'note': 'reverse search supports images only'}
        credibility = assess_credibility(source_url or '') if source_url else {'score': 50, 'reasons': ['No source URL provided'], 'domain': ''}
        ocr = ocr_summary(file_path) if media_type == 'image' else {'enabled': False, 'note': 'OCR supports images only in this scaffold'}
        factcheck = build_factcheck_context(ocr.get('text') or '')

        detection_score = float(analysis.anomaly_score * 100.0)
        source_score = self._source_score(credibility, provenance, reverse_search)
        explanation_confidence = 75.0 if explanation.get('used_llm') else 55.0
        overall = float(max(0.0, min(100.0, (detection_score * 0.5 + source_score * 0.3 + explanation_confidence * 0.2))))

        return VerificationPayload(
            analysis=asdict(analysis),
            explanation=explanation,
            provenance=provenance,
            metadata=metadata,
            reverse_search=reverse_search,
            credibility=credibility,
            ocr=ocr,
            factcheck=factcheck,
            score=MediaSyntheticScore(overall=overall, detection=detection_score, source=source_score, explanation_confidence=explanation_confidence),
        )

    def to_dict(self, payload: VerificationPayload) -> Dict[str, Any]:
        return {
            'score': {
                'overall': round(payload.score.overall, 2),
                'detection': round(payload.score.detection, 2),
                'source': round(payload.score.source, 2),
                'explanation_confidence': round(payload.score.explanation_confidence, 2),
            },
            'analysis': payload.analysis,
            'explanation': payload.explanation,
            'provenance': payload.provenance,
            'metadata': payload.metadata,
            'reverse_search': payload.reverse_search,
            'credibility': payload.credibility,
            'ocr': payload.ocr,
            'factcheck': payload.factcheck,
        }
