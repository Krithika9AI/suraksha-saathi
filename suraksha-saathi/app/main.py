"""FastAPI service: POST /analyze with text, or /analyze-image with a screenshot (OCR)."""
import io
from dataclasses import asdict

from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel

from app.detector import analyze

app = FastAPI(title="Suraksha Saathi", version="0.1.0")


class TextIn(BaseModel):
    text: str
    lang: str = "en"  # en | hi | ta


@app.post("/analyze")
def analyze_text(body: TextIn):
    return asdict(analyze(body.text, body.lang))


@app.post("/analyze-image")
async def analyze_image(file: UploadFile = File(...), lang: str = "en"):
    import pytesseract  # needs the tesseract binary (+ tam/hin language data)
    from PIL import Image

    image = Image.open(io.BytesIO(await file.read()))
    code = {"en": "eng", "hi": "hin", "ta": "tam"}.get(lang, "eng")
    text = pytesseract.image_to_string(image, lang=code)
    return {"extracted_text": text, **asdict(analyze(text, lang))}


@app.get("/health")
def health():
    return {"status": "ok"}
