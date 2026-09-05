# PromptWars Media Verification Platform

End-to-end media verification platform with detection, explanation, and source-trace verification layers.

## Features

- Upload and analyze images, audio, and video
- Synthetic manipulation score with breakdown
- Face detection and region localization
- Image manipulation heatmap
- Plain-English explanation via Gemini API
- Reverse image search
- EXIF/metadata inspection
- OCR text extraction
- Fact-check context

## Quick start

### Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python3 app.py
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`.

## Environment variables

| Variable | Purpose |
|---------|---------|
| `GEMINI_API_KEY` | Gemini API key for explanation generation |
| `GEMINI_MODEL` | Gemini model name |
| `USE_GEMINI` | Set to `true` to enable Gemini explanations |
| `SERPAPI_KEY` | SerpAPI key for reverse image/search |
| `FLASK_SECRET_KEY` | Flask secret key |
| `MAX_CONTENT_LENGTH` | Upload limit in bytes |

## API

- `POST /api/analyze` — analyze uploaded media
- `POST /api/reverse-search` — reverse image search
- `POST /api/provenance` — provenance inspection

## Notes

- Analysis is signal-based and lightweight.
- Gemini is optional; without it, explanations use a deterministic fallback.
- Do not commit real secrets. `.env` is gitignored.
