# main.py ──────────────────────────────────────────────────────────────
from fastapi import FastAPI, Body, HTTPException
import shutil, os
from pipeline import run_pipeline  # ← your existing heavy pipeline
from reel_utils import convert_video_to_wav  # ← helper from earlier answer

app = FastAPI(title="One-shot reel-to-pipeline")


@app.post("/process")
async def process(payload: dict = Body(...)):
    mock = payload.get("mock", False)
    if mock:
        wav_path = os.path.abspath("audio.wav")
        tmp_dir = os.path.dirname(wav_path)
    else:
        url = payload.get("url")
        if not url:
            raise HTTPException(400, "JSON body must contain a 'url' field")
        try:
            print(f"Downloading reel from {url}...")
            wav_path = convert_video_to_wav(url)
            tmp_dir = os.path.dirname(wav_path)
        except RuntimeError as e:
            raise HTTPException(400, str(e))

    try:
        result = run_pipeline(wav_path)
        return result
    finally:
        if not mock:
            shutil.rmtree(tmp_dir, ignore_errors=True)
