from __future__ import annotations

import os
import base64
import mimetypes
from typing import Any, Dict, List, Optional

import requests


def _mime_for(path: str) -> str:
    mime, _ = mimetypes.guess_type(path)
    return mime or 'application/octet-stream'


def _serp_reverse_image(image_bytes: bytes, api_key: str, limit: int = 8) -> Dict[str, Any]:
    if not api_key:
        return {'enabled': False, 'note': 'SERPAPI_KEY not configured'}
    try:
        b64 = base64.b64encode(image_bytes).decode('utf-8')
        resp = requests.post(
            'https://serpapi.com/search',
            data={
                'engine': 'google_reverse_image',
                'image': b64,
                'api_key': api_key,
            },
            timeout=25,
        )
        resp.raise_for_status()
        data = resp.json()
        matches: List[Dict[str, Any]] = []
        for item in data.get('image_results', [])[:limit]:
            matches.append({
                'title': item.get('title'),
                'link': item.get('link'),
                'source': item.get('source'),
                'thumbnail': item.get('thumbnail'),
            })
        return {'enabled': True, 'matches': matches}
    except Exception as exc:
        return {'enabled': False, 'error': str(exc)}


def reverse_image_search(path: str, api_key: Optional[str] = None) -> Dict[str, Any]:
    key = api_key or os.getenv('SERPAPI_KEY')
    with open(path, 'rb') as f:
        image_bytes = f.read()
    return _serp_reverse_image(image_bytes, key)


def reverse_search_summary(path: str) -> Dict[str, Any]:
    mime = _mime_for(path)
    if mime.startswith('image'):
        return reverse_image_search(path)
    return {'enabled': False, 'note': 'Reverse search supports images only in this scaffold.', 'media_type': mime}
