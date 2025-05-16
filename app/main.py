# main.py ──────────────────────────────────────────────────────────────
from fastapi import FastAPI, Body, HTTPException
import shutil, os
from pipeline import run_pipeline  # ← your existing heavy pipeline
from reel_utils import convert_video_to_wav  # ← helper from earlier answer

app = FastAPI(title="One-shot reel-to-pipeline")


@app.post("/process")
async def process(payload: dict = Body(...)):
    """
    Request body **must** be: { "url": "https://www.instagram.com/reel/ABC123xyz/" }

    Example:
        curl -X POST http://host:port/process \
             -H "Content-Type: application/json" \
             -d '{"url": "https://www.instagram.com/reel/ABC123xyz/"}'
    """
    url = payload.get("url")
    if not url:
        raise HTTPException(400, "JSON body must contain a 'url' field")

    # 1️⃣  Download reel → WAV in a temp directory
    try:
        print(f"Downloading reel from {url}...")
        wav_path = convert_video_to_wav(url)  # returns /tmp/reel_xxx/xxxx.wav
        tmp_dir = os.path.dirname(wav_path)
    except RuntimeError as e:
        raise HTTPException(400, str(e))

    # 2️⃣  Run Whisper + downstream LLMs
    try:
        result = run_pipeline(wav_path)  # ← your function
        return result  # FastAPI auto-serialises dict → JSON
    finally:
        # 3️⃣  Always clean up temp files
        shutil.rmtree(tmp_dir, ignore_errors=True)
