from __future__ import annotations

import os
import re
from typing import Any, Dict, List, Optional

import requests


def _serp_factcheck(query: str, api_key: Optional[str] = None) -> Dict[str, Any]:
    key = api_key or os.getenv('SERPAPI_KEY')
    if not key:
        return {'enabled': False, 'note': 'SERPAPI_KEY not configured'}
    try:
        resp = requests.get(
            'https://serpapi.com/search',
            params={'engine': 'google', 'q': query, 'api_key': key},
            timeout=20,
        )
        resp.raise_for_status()
        data = resp.json()
        results: List[Dict[str, Any]] = []
        for item in data.get('organic_results', [])[:6]:
            results.append({'title': item.get('title'), 'link': item.get('link'), 'snippet': item.get('snippet')})
        return {'enabled': True, 'results': results}
    except Exception as exc:
        return {'enabled': False, 'error': str(exc)}


def build_factcheck_context(text: str, max_queries: int = 3) -> Dict[str, Any]:
    text = (text or '').strip()
    if not text:
        return {'enabled': False, 'note': 'No text available for fact-check context.'}
    sentences = re.split(r'(?<=[.!?])\s+', text)
    queries = [s for s in sentences[:max_queries] if len(s.split()) >= 4][:max_queries]
    if not queries:
        queries = [text[:140]]
    contexts = []
    for q in queries:
        ctx = _serp_factcheck(q)
        contexts.append({'query': q, 'context': ctx})
    return {'enabled': True, 'queries': queries, 'contexts': contexts}
