import openai, time

client = openai.OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",
)
# MODEL = "gemma3:27b"                   # well performing
MODEL = "deepseek-r1:1.5b"               # reasing
# MODEL = "dongheechoi/meerkat:latest"   # based on medical data: https://www.nature.com/articles/s41746-025-01653-8

# Improved prompt
CHECK_PROMPT_TMPL = (
    "You are a medical fact-checker.\n"
    "Given the statement below, reply ONLY with a single line in this format:\n"
    "[INCORRECT/CORRECT: <correctness score>]\n"
    # "Where VERDICT is either \"CORRECT\" or \"INCORRECT\". Score is an integer from 0 (not correct) to 100 (completely correct).\n"
    "Do NOT explain. Do NOT say what you have to do. Do NOT repeat the statement. Do NOT add any extra text.\n"
    "Example: [INCORRECT: 0]\n"
    "\n"
    "STATEMENT:\"\n{statement}\n\""
)

sample_statement = "Doing one hour of sport every day is super healthy, but will give you cancer in the long run."

print(f"Checking: {sample_statement}")
t0 = time.time()
response = client.chat.completions.create(
    model=MODEL,
    temperature=0, 
    max_tokens=750,
    messages=[{"role": "user", "content": CHECK_PROMPT_TMPL.format(statement=sample_statement)}],
)
t1 = time.time()

ans = response.choices[0].message.content.strip()
print(f"Model output: '{ans}'")
print(f"⏱ {t1-t0:.2f} s")
