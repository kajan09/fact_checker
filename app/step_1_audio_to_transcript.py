#!/usr/bin/env python3
from typing import Any, Dict, Union
import argparse, datetime as dt, json, re, sys
from pathlib import Path

import whisper   # pip install -U openai-whisper

WHISPER_MODEL_NAME = "small"     #tiny, base, small, medium, large
TRAILING_COMMAS_RE = re.compile(r",\s*(?=[\]}])")  # tolerate trailing commas

# ───────── helpers ─────────
def load_json_relaxed(path: Union[str, Path]) -> Dict[str, Any]:
    raw = Path(path).read_text(encoding="utf-8")
    return json.loads(TRAILING_COMMAS_RE.sub("", raw))

def write_json(path: Union[str, Path], data: Dict[str, Any]) -> None:
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def transcribe_audio(audio_path: Union[str, Path]) -> str:
    model = whisper.load_model(WHISPER_MODEL_NAME)
    res   = model.transcribe(str(audio_path), fp16=True)
    text  = res["text"].strip()
    if res.get("language", "en") != "en":
        res  = model.transcribe(str(audio_path), task="translate", fp16=True)
        text = res["text"].strip()
    return text

# ───────── core ─────────
def update_transcript(json_in: str, audio_in: str) ->  Dict[str, Any]:
    data             = load_json_relaxed(json_in)
    data["transcript"] = transcribe_audio(audio_in)
    data["generated_at"] = dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    return data
