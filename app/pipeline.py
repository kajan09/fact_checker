# pipeline.py
import os, re
from startup import whisper_model, openai_client, LLM_MODEL

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
    transcript = whisper_model.transcribe(tmp_path, task="translate", fp16=True)["text"]

    # 2️⃣ Fact-check via Ollama-served model
    prompt = CHECK_PROMPT_TMPL.format(statement=transcript)
    raw = openai_client.chat.completions.create(
        model=LLM_MODEL,
        temperature=0,
        max_tokens=5,
        messages=[{"role": "user", "content": prompt}],
    ).choices[0].message.content.strip()

    m = score_re.search(raw)
    score = int(m.group(1)) if m and 0 <= int(m.group(1)) <= 100 else None

    return {
        "transcript": transcript,
        "fact_score": score,
        "raw_factcheck_reply": raw,
    }
