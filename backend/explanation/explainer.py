from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class ExplanationRequest:
    media_type: str
    score: float
    top_signals: List[tuple[str, float]]
    artifact_findings: List[Dict[str, Any]]
    face_detections: List[Dict[str, Any]]
    provenance: Optional[Dict[str, Any]] = None
    reverse_search: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


class ExplanationLayer:
    """Explanation layer with optional Gemini API and template fallback."""
    
    def __init__(self, use_gemini: bool = False, gemini_model: Optional[str] = None):
        self.use_gemini = use_gemini
        self.gemini_model = gemini_model or os.getenv('GEMINI_MODEL', 'gemini-1.5-flash')
        self._client = None
    
    def _load_client(self):
        if self._client is not None:
            return self._client
        if not self.use_gemini:
            return None
        try:
            api_key = os.getenv('GEMINI_API_KEY')
            if not api_key:
                return None
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            self._client = genai.GenerativeModel(self.gemini_model)
            return self._client
        except Exception as exc:
            print(f'Gemini init failed: {exc}')
            return None
    
    def _gemini_generate(self, prompt: str) -> str:
        model = self._load_client()
        if model is None:
            return self._template_fallback(prompt)
        try:
            response = model.generate_content(prompt)
            text = getattr(response, 'text', None)
            if text:
                return text.strip()
            return self._template_fallback(prompt)
        except Exception as exc:
            print(f'Gemini generation failed: {exc}')
            return self._template_fallback(prompt)
    
    def _template_fallback(self, prompt: str) -> str:
        return (
            'Analysis suggests mixed evidence. The top signals indicate localized anomalies. '
            'For stronger verification, check provenance metadata, reverse-search context, and original source.'
        )
    
    def _score_verdict(self, score: float) -> str:
        if score < 30:
            return 'Low manipulation likelihood'
        if score < 60:
            return 'Mixed signals; some anomalies detected'
        return 'High manipulation likelihood; manual review recommended'
    
    def _top_signal_lines(self, signals: List[tuple[str, float]], limit: int = 5) -> List[str]:
        out = []
        for name, value in sorted(signals, key=lambda x: x[1], reverse=True)[:limit]:
            if value < 0.25:
                label = 'weak'
            elif value < 0.6:
                label = 'moderate'
            else:
                label = 'strong'
            out.append(f'- {name}: {label} ({value:.2f})')
        return out
    
    def _provenance_lines(self, provenance: Optional[Dict[str, Any]]) -> List[str]:
        if not provenance:
            return ['- Provenance: no data available']
        if provenance.get('available'):
            return ['- Provenance: C2PA manifest detected.']
        return [f"- Provenance: unavailable ({provenance.get('error', 'unknown')})"]
    
    def _reverse_lines(self, reverse: Optional[Dict[str, Any]]) -> List[str]:
        if not reverse:
            return ['- Reverse search: not available']
        if reverse.get('enabled'):
            matches = reverse.get('matches', [])
            if matches:
                return [f'- Reverse search: {len(matches)} matching source(s) found.']
            return ['- Reverse search: no matching sources found.']
        return [f"- Reverse search: disabled ({reverse.get('note') or reverse.get('error') or 'not configured'})"]
    
    def _build_prompt(self, req: ExplanationRequest) -> str:
        signal_lines = '\n'.join(self._top_signal_lines(req.top_signals))
        prov_lines = '\n'.join(self._provenance_lines(req.provenance))
        rev_lines = '\n'.join(self._reverse_lines(req.reverse_search))
        return (
            'You are a media forensics assistant. Write a concise, plain-English explanation '
            'of the analysis result. Do not invent facts. Keep it to 3-6 sentences.\n\n'
            f"Media type: {req.media_type}\n"
            f"Score: {req.score:.1f}/100 ({self._score_verdict(req.score)})\n"
            f"Top signals:\n{signal_lines}\n"
            f"{prov_lines}\n"
            f"{rev_lines}\n\n"
            'Explanation:'
        )
    
    def explain(self, req: ExplanationRequest) -> Dict[str, Any]:
        prompt = self._build_prompt(req)
        plain_english = self._gemini_generate(prompt)
        top_signals = [
            {'name': name, 'score': round(float(value), 4), 'level': 'weak' if value < 0.25 else 'moderate' if value < 0.6 else 'strong'}
            for name, value in req.top_signals
        ]
        return {
            'score': round(float(req.score), 2),
            'verdict': self._score_verdict(req.score),
            'plain_english': plain_english,
            'top_signals': top_signals,
            'used_llm': bool(self._load_client()),
        }
