#!/usr/bin/env python3
import openai, time, re

# ── 1.  Client ──────────────────────────────────────────────────────────────
client = openai.OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",
)
MODEL = "meditron-70bq4:latest"  # or any other loaded model

# Warm-load
client.chat.completions.create(
    model=MODEL, temperature=0,
    messages=[{"role": "user", "content": "ping"}],
    max_tokens=1,
)

# ── 2.  Fact-check prompt ───────────────────────────────────────────────────
CHECK_PROMPT_TMPL = (
    "You are a medical fact-checker.\n"
    "Given the statement below, reply ONLY with an integer score from 0 (false) to 100 (true).\n"
    "NO verdict, NO explanation, ONLY the number.\n\n"
    "STATEMENT:\n{statement}\n"
)
CHECK_PROMPT_TMPL2 = (
    "You are a professional fact‑checker. Classify the statement as true, false, or uncertain. "
    "Return ONLY valid JSON of the form: {\n  \"verdict\": \"true|false|uncertain\",\n  \"rationale\": <string>,\n  \"confidence\": <float between 0 and 1>\n} \n\nSTATEMENT:\n{statement}"
)

sample_statement = "Smoking crack gives you cancer."

score_re = re.compile(r"\b([0-9]{1,3})\b")

print(f"Checking: {sample_statement}")
t0 = time.time()
print(f"⏱ {t1-t0:.2f} s")
ans = client.chat.completions.create(
    model=MODEL,
    temperature=0.1,
    max_tokens=5,
    messages=[{"role": "user", "content": CHECK_PROMPT_TMPL.format(statement=sample_statement)}],
).choices[0].message.content.strip()
t1 = time.time()

print(f"⏱ {t1-t0:.2f} s")
#print(f"Response: '{ans}'")



m = score_re.search(ans)
if m and 0 <= int(m.group(1)) <= 100:
    print(f"Score: {int(m.group(1))}")
else:
    print(f"Could not parse score: '{ans}'")
