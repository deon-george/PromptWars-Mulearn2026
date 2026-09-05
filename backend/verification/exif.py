from __future__ import annotations

import os
import json
from typing import Any, Dict, Optional

from PIL import Image
from PIL.ExifTags import TAGS


def _read_exif(path: str) -> Dict[str, Any]:
    try:
        image = Image.open(path)
        raw = image._getexif() or {}
        out: Dict[str, Any] = {}
        for tag, value in raw.items():
            label = TAGS.get(tag, str(tag))
            try:
                json.dumps(value)
                out[label] = value
            except Exception:
                out[label] = str(value)
        return out
    except Exception as exc:
        return {'error': str(exc)}


def inspect_exif(path: str) -> Dict[str, Any]:
    exif = _read_exif(path)
    return {
        'exif': exif,
        'has_metadata': bool(exif) and 'error' not in exif,
        'notes': 'EXIF inspection complete.',
    }


def inspect_metadata(path: str, media_type: Optional[str] = None) -> Dict[str, Any]:
    result: Dict[str, Any] = {'media_type': media_type}
    if media_type == 'image':
        result['exif'] = _read_exif(path)
    if media_type in ('audio', 'video'):
        result['stream_metadata'] = {'note': 'Stream metadata parsing not implemented in this scaffold.'}
    return result
