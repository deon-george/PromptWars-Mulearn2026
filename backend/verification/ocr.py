from __future__ import annotations

import os
from typing import Any, Dict, List, Optional


def _run_pytesseract(path: str) -> Dict[str, Any]:
    try:
        import pytesseract
        from PIL import Image
    except ImportError as exc:
        return {'enabled': False, 'error': f'pytesseract unavailable: {exc}'}
    try:
        image = Image.open(path)
        text = pytesseract.image_to_string(image)
        return {'enabled': True, 'text': text, 'engine': 'pytesseract'}
    except Exception as exc:
        return {'enabled': False, 'error': str(exc)}


def _run_easyocr(path: str) -> Dict[str, Any]:
    try:
        import easyocr
    except ImportError as exc:
        return {'enabled': False, 'error': f'easyocr unavailable: {exc}'}
    try:
        reader = easyocr.Reader(['en'], gpu=False)
        result = reader.readtext(path, detail=0)
        return {'enabled': True, 'text': '\n'.join(result), 'engine': 'easyocr'}
    except Exception as exc:
        return {'enabled': False, 'error': str(exc)}


def extract_text(path: str) -> Dict[str, Any]:
    res = _run_pytesseract(path)
    if res.get('enabled') and res.get('text'):
        return res
    if res.get('enabled'):
        fallback = _run_easyocr(path)
        if fallback.get('enabled'):
            return fallback
        return res
    return _run_easyocr(path)


def ocr_summary(path: str) -> Dict[str, Any]:
    data = extract_text(path)
    text = (data.get('text') or '').strip()
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return {
        'engine': data.get('engine'),
        'enabled': data.get('enabled', False),
        'text': text,
        'line_count': len(lines),
        'preview': '\n'.join(lines[:20]),
        'error': data.get('error'),
    }
