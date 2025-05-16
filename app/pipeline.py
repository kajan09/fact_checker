# pipeline.py
import os, re
from step_1_audio_to_transcript import update_transcript
from step_2_transcript_to_statement import update_statements

CHECK_PROMPT_TMPL = (
    "You are a medical fact-checker.\n"
    "Given the statement below, reply ONLY with an integer score from 0 (false) to 100 (true).\n"
    "NO verdict, NO explanation, ONLY the number.\n\n"
    "STATEMENT:\n{statement}\n"
)
score_re = re.compile(r"\b([0-9]{1,3})\b")

def run_pipeline(tmp_path: str) -> dict:
    """
    1) Transcribe with Whisper
    2) Feed the transcript to an LLM (e.g. fact-check, summary, follow-up Q&A…)
    3) Return a dict you’ll JSON-encode later
    """
    # 1️⃣ Whisper
    transcript = update_transcript("json_example.json", tmp_path)
    statments = update_statements(transcript)
    print(f"Transcription: {statments}")
