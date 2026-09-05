from __future__ import annotations

import os
from typing import Any, Dict, Optional

import requests


def reverse_image_search(path: str, api_key: Optional[str] = None) -> Dict[str, Any]:
    key = api_key or os.getenv('SERPAPI_KEY')
    if not key:
        return {'enabled': False, 'note': 'SERPAPI_KEY not configured'}
    try:
        with open(path, 'rb') as f:
            resp = requests.post(
                'https://serpapi.com/search',
                data={
                    'engine': 'google_reverse_image',
                    'api_key': key,
                },
                files={'image': ('image', f, 'application/octet-stream')},
                timeout=25,
            )
        resp.raise_for_status()
        data = resp.json()
        matches = []
        for item in data.get('image_results', [])[:8]:
            matches.append({
                'title': item.get('title'),
                'link': item.get('link'),
                'source': item.get('source'),
                'thumbnail': item.get('thumbnail'),
            })
        return {'enabled': True, 'matches': matches}
    except Exception as exc:
        return {'enabled': False, 'error': str(exc)}


def reverse_search_summary(path: str) -> Dict[str, Any]:
    if path.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.bmp', '.tiff')):
        return reverse_image_search(path)
    return {'enabled': False, 'note': 'Reverse search supports images only in this scaffold.', 'media_type': 'unknown'}
