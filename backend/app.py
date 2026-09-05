from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import uuid
import json
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_CONTENT_LENGTH', 200 * 1024 * 1024))
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key')
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, 'uploads')
ANALYSIS_DIR = os.path.join(BASE_DIR, 'static', 'analysis')
for d in (UPLOAD_DIR, ANALYSIS_DIR):
    os.makedirs(d, exist_ok=True)

ALLOWED_IMAGE = {'png', 'jpg', 'jpeg', 'webp', 'bmp', 'tiff'}
ALLOWED_AUDIO = {'mp3', 'wav', 'ogg', 'flac', 'm4a', 'aac'}
ALLOWED_VIDEO = {'mp4', 'mov', 'avi', 'mkv', 'webm'}
ALLOWED_EXTENSIONS = ALLOWED_IMAGE | ALLOWED_AUDIO | ALLOWED_VIDEO

from analysis.detector import analyze
from analysis.model_setup import ensure_face_models
from verification.orchestrator import VerificationAssistant

try:
    ensure_face_models()
except Exception:
    pass


def _extension(filename: str) -> str:
    return (filename.rsplit('.', 1)[-1] if '.' in filename else '').lower()


def _media_type(filename: str):
    ext = _extension(filename)
    if ext in ALLOWED_IMAGE:
        return 'image'
    if ext in ALLOWED_AUDIO:
        return 'audio'
    if ext in ALLOWED_VIDEO:
        return 'video'
    return None


def _allowed(filename: str) -> bool:
    return _media_type(filename) is not None


def _save_upload(file_storage):
    original = secure_filename(file_storage.filename)
    ext = _extension(original)
    name = f"{uuid.uuid4().hex}.{ext}"
    abs_path = os.path.join(UPLOAD_DIR, name)
    file_storage.save(abs_path)
    static_path = f"/static/uploads/{name}"
    return abs_path, static_path


@app.get('/')
def index():
    return render_template('index.html')


@app.get('/api/health')
def health():
    return jsonify({'status': 'ok'})


@app.post('/api/analyze')
def analyze_route():
    if 'file' not in request.files:
        return jsonify({'error': 'missing file field'}), 400
    upload = request.files['file']
    if not upload.filename:
        return jsonify({'error': 'empty filename'}), 400
    if not _allowed(upload.filename):
        return jsonify({'error': 'unsupported media type'}), 400

    abs_path, static_path = _save_upload(upload)
    media_type = _media_type(upload.filename)

    try:
        analysis = analyze(abs_path, media_type)
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 400
    except Exception as exc:
        return jsonify({'error': f'analysis_failed: {exc}'}), 500

    use_gemini = os.getenv('USE_GEMINI', 'false').lower() in ('1', 'true', 'yes')
    gemini_model = os.getenv('GEMINI_MODEL')
    assistant = VerificationAssistant(use_gemini=use_gemini, gemini_model=gemini_model)
    payload = assistant.synthesize(analysis, abs_path, media_type)

    result = {
        'media_type': media_type,
        'filename': secure_filename(upload.filename),
        'file_path': static_path,
        **assistant.to_dict(payload),
    }

    analysis_name = f"{uuid.uuid4().hex}.json"
    analysis_path = os.path.join(ANALYSIS_DIR, analysis_name)
    with open(analysis_path, 'w', encoding='utf-8') as f:
        json.dump(result, f)
    result['analysis_path'] = f"/static/analysis/{analysis_name}"
    return jsonify(result)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)), debug=True)
