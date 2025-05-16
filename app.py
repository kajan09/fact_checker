from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import whisper
import tempfile
import shutil
import os



app = FastAPI(
    title="Whisper Transcription API",
    description="Transcribes audio or video files using OpenAI Whisper.",
    version="1.0.0"
)

# Load model once at startup
model = whisper.load_model("tiny.en")  # Or "base", "small", etc.

@app.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    # Save to temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[-1]) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    try:
        result = model.transcribe(tmp_path, fp16=True)
        return JSONResponse(content={"text": result["text"]})
    finally:
        os.remove(tmp_path)  # Clean up temp file
