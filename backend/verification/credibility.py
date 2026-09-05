from __future__ import annotations

import os
import re
from typing import Any, Dict, Optional

import requests
from bs4 import BeautifulSoup


TRUSTED_TLDS = {'.gov', '.edu', '.ac.in', '.ac.uk', '.who.int'}
SUSPICIOUS_SIGNALS = ['clickbait', 'shocking', "you won't believe", 'secret', 'miracle']


def _domain(url: str) -> str:
    try:
        from urllib.parse import urlparse
        return urlparse(url).netloc.lower()
    except Exception:
        return ''


def _tld(domain: str) -> str:
    for tld in TRUSTED_TLDS:
        if domain.endswith(tld):
            return tld
    return ''


def _heuristic_credibility(url: str) -> Dict[str, Any]:
    domain = _domain(url)
    tld = _tld(domain)
    score = 50
    reasons: list[str] = []
    if tld:
        score += 25
        reasons.append(f'Trusted domain extension: {tld}')
    if any(signal in url.lower() for signal in SUSPICIOUS_SIGNALS):
        score -= 20
        reasons.append('URL contains clickbait-style wording')
    score = max(0, min(100, score))
    return {'domain': domain, 'score': score, 'reasons': reasons}


def _serp_source_context(url: str, api_key: Optional[str] = None) -> Dict[str, Any]:
    key = api_key or os.getenv('SERPAPI_KEY')
    if not key:
        return {'enabled': False, 'note': 'SERPAPI_KEY not configured'}
    try:
        resp = requests.get(
            'https://serpapi.com/search',
            params={'engine': 'google', 'q': f'site:{_domain(url)}', 'api_key': key},
            timeout=20,
        )
        resp.raise_for_status()
        data = resp.json()
        snippets = []
        for item in data.get('organic_results', [])[:5]:
            snippets.append({'title': item.get('title'), 'link': item.get('link'), 'snippet': item.get('snippet')})
        return {'enabled': True, 'snippets': snippets}
    except Exception as exc:
        return {'enabled': False, 'error': str(exc)}


def assess_credibility(url: str) -> Dict[str, Any]:
    heuristic = _heuristic_credibility(url)
    serp = _serp_source_context(url)
    base = heuristic['score']
    modifier = 0
    if serp.get('enabled') and serp.get('snippets'):
        modifier += 10
    score = max(0, min(100, base + modifier))
    return {
        'url': url,
        'score': score,
        'reasons': heuristic['reasons'],
        'domain': heuristic['domain'],
        'serp_context': serp,
    }
