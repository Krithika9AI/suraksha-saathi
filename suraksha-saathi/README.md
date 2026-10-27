# Suraksha Saathi — Multilingual AI Scam Shield

An AI safety net that helps elders and first-time digital users in India recognise online fraud (digital arrest, KYC, UPI collect requests, lottery and job-task scams) **at the moment it happens**, in Tamil, Hindi or English.

Built for *Hack for Social Cause* (VBYLD 2026) — Theme: Digital Safety & Cyber Fraud Awareness.

## Features
- Paste/forward a message, or upload a screenshot (OCR) to get a risk score (LOW / MEDIUM / HIGH).
- Scam-type detection with plain-language reasons.
- Localised next-step advice (call 1930, report on cybercrime.gov.in).
- Optional trusted-contact alert (roadmap), voice call analysis via Whisper (roadmap).

## Quick start
```bash
git clone <your-repo-url> && cd suraksha-saathi
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
# For screenshot OCR install Tesseract + language data:
#   sudo apt install tesseract-ocr tesseract-ocr-tam tesseract-ocr-hin
uvicorn app.main:app --reload
```
Open **http://localhost:8000** for the web app: paste a message (or tap an example), pick English, Tamil or Hindi, and press Check. The result shows a colour-coded risk level, score, plain reasons and what to do, and a Listen button reads it aloud if your browser has a voice for that language.

API (optional):
```bash
curl -X POST localhost:8000/analyze -H "Content-Type: application/json" \
  -d '{"text":"You are under digital arrest. Do not tell anyone and pay immediately.","lang":"en"}'
```
Interactive API docs: http://localhost:8000/docs

## Environment variables
None are required for the baseline. Optional (roadmap features):

| Variable | Purpose |
|---|---|
| `TESSDATA_PREFIX` | Custom path to Tesseract language data |
| `WHISPER_MODEL` | Whisper model size for call audio (e.g. `small`) |
| `ALERT_WEBHOOK_URL` | Endpoint for trusted-contact alerts |

## Tests
```bash
pytest -q
```
`sample_data/sample_messages.csv` holds labelled example messages used by the tests.

## Project structure
```
app/detector.py   scoring engine (rules + optional ML score)
app/main.py       FastAPI endpoints and web page route
app/static/       web app (index.html)
tests/            unit tests
sample_data/      labelled sample messages
TECH_DESIGN.md    architecture and design decisions
```

## Privacy
No messages are stored by default. Analysis is stateless; phone numbers and UPI IDs are never logged.

## License
MIT — see `LICENSE`.
