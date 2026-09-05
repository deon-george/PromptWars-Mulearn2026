import os
import requests
from typing import Optional


MODEL_DIR = os.path.join(os.path.dirname(__file__), 'models')
PROTOTXT_URL = 'https://raw.githubusercontent.com/opencv/opencv/master/samples/dnn/face_detector/deploy.prototxt'
WEIGHTS_URL = 'https://github.com/opencv/opencv_3rdparty/raw/dnn_samples_face_detector_20170830/res10_300x300_ssd_iter_140000.caffemodel'


def _download(url: str, dest: str):
    if os.path.exists(dest) and os.path.getsize(dest) > 10000:
        return
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    with open(dest, 'wb') as f:
        f.write(r.content)


def ensure_face_models(model_dir: Optional[str] = None) -> str:
    base = model_dir or MODEL_DIR
    os.makedirs(base, exist_ok=True)
    proto = os.path.join(base, 'deploy.prototxt')
    weights = os.path.join(base, 'res10_300x300_ssd_iter_140000.caffemodel')
    _download(PROTOTXT_URL, proto)
    _download(WEIGHTS_URL, weights)
    return base
